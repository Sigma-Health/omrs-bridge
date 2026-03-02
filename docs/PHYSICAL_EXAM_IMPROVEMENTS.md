# Physical Exam Endpoint — Pending Improvements

Tracked improvements identified after initial implementation of `POST/GET/PATCH/DELETE /api/v1/physical-exam/`.

---

## 1. Schema & Validation

### 1a. Enforce `visit_id` or `visit_uuid` at schema level
**File:** `app/schemas/physical_exam.py`

Currently `_resolve_visit` in the CRUD raises a `ValueError` if neither field is provided. This should be caught earlier at the Pydantic validation layer so the client gets a `422 Unprocessable Entity` instead of a `404`.

```python
from pydantic import model_validator

@model_validator(mode="after")
def require_visit_identifier(self) -> "PhysicalExamCreate":
    if not self.visit_id and not self.visit_uuid:
        raise ValueError("Either visit_id or visit_uuid must be provided")
    return self
```

### 1b. Reject empty `notes` list
**File:** `app/schemas/physical_exam.py`

An empty `notes: []` body currently reaches the DB and creates an encounter with no observations. Add a field validator:

```python
from pydantic import field_validator

@field_validator("notes")
@classmethod
def notes_must_not_be_empty(cls, v):
    if not v:
        raise ValueError("notes must contain at least one entry")
    return v
```

---

## 2. CRUD Correctness

### 2a. `update_exam_note` — stamp `changed_by` and `date_changed`
**File:** `app/crud/physical_exam.py` → `update_exam_note`

When patching an obs, OpenMRS convention requires setting audit fields. The `ExamNoteUpdate` schema needs an `editor` field (the user ID making the change), and the CRUD should apply:

```python
obs.changed_by = payload.editor
obs.date_changed = datetime.utcnow()
```

**Schema change needed:** add `editor: Optional[int] = None` to `ExamNoteUpdate`.

### 2b. `update_exam_note` — stale encounter on hydration
**File:** `app/crud/physical_exam.py` → `update_exam_note`

The `encounter` variable is fetched before the commit and used for `_hydrate_obs` after the commit. While encounter data rarely changes, the guard `if not encounter` re-fetches only in the failure case. The encounter fetch should move to after `db.commit()` / `db.refresh(obs)` to be consistent.

### 2c. `_hydrate_obs` — N+1 query problem
**File:** `app/crud/physical_exam.py` → `_hydrate_obs`

Each call to `_hydrate_obs` issues 4 separate SQL queries:
1. Concept name lookup
2. Creator name lookup
3. Encounter UUID lookup
4. Visit UUID lookup

For GET endpoints that return many observations (e.g. a visit with 20+ notes), this produces up to 80 queries. These should be consolidated into a single JOIN query, similar to the pattern used in the vitals SQL files.

---

## 3. Missing Functionality

### 3a. `void_reason` on DELETE
**File:** `app/crud/physical_exam.py` → `delete_exam_note`  
**File:** `app/api/physical_exam.py` → `delete_physical_exam_note`

The DELETE endpoint accepts no request body. OpenMRS convention expects a `void_reason` to be stored when voiding a record. A minimal request body should be added:

```python
class ExamNoteVoid(BaseModel):
    void_reason: Optional[str] = None
    voided_by: Optional[int] = None
```

And the CRUD should apply:
```python
obs.void_reason = payload.void_reason
obs.voided_by = payload.voided_by
```

---

## 4. Configuration

### 4a. `PHYSICAL_EXAM_CONCEPT_ID` as a list
**File:** `app/config.py`

Currently `physical_exam_concept_id` is a single integer. If different exam sections use different concept IDs (e.g. chief complaint, exam findings, assessment), this should become a comma-separated list — following the same pattern as `VITAL_SIGNS_CONCEPT_IDS`.

### 4b. `CONSULTATION_ENCOUNTER_ROLE_ID` env var
**File:** `app/config.py`, `docker-compose.yml`, `docker-compose.bahmni.yml`

The `encounter_role_id` defaults to `1` both in the schema and in the CRUD fallback. This should be a configurable env var:

```
CONSULTATION_ENCOUNTER_ROLE_ID=1
```

---

## 5. API / REST Conventions

### 5a. `DELETE` should return HTTP 204
**File:** `app/api/physical_exam.py` → `delete_physical_exam_note`

REST convention for a successful delete/void is `204 No Content` with no response body. Currently returns a JSON object. Change to:

```python
from fastapi import Response

@router.delete("/{obs_id}", status_code=204)
async def delete_physical_exam_note(...):
    ...
    physical_exam.delete_exam_note(db, obs_id)
    return Response(status_code=204)
```

The CRUD `delete_exam_note` return value can be dropped.

---

## Priority Order

| # | Item | Priority |
|---|------|----------|
| 1 | 3a — `void_reason` on DELETE | High |
| 2 | 2a — `changed_by`/`date_changed` on PATCH | High |
| 3 | 1a — `model_validator` for visit identifier | Medium |
| 4 | 1b — reject empty `notes` | Medium |
| 5 | 5a — `DELETE` returns 204 | Medium |
| 6 | 2b — stale encounter on hydration | Low |
| 7 | 2c — N+1 queries in `_hydrate_obs` | Low |
| 8 | 4a — `physical_exam_concept_id` as list | Low |
| 9 | 4b — `CONSULTATION_ENCOUNTER_ROLE_ID` env var | Low |
