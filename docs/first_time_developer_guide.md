# OpenMRS Bridge API - First-Time Developer Guide

This guide is for new developers joining the project and getting productive quickly with minimal back-and-forth.

## 1. What This Project Is

`bridge` is a FastAPI service that exposes authenticated REST endpoints over an OpenMRS/Bahmni MySQL database.

Core responsibilities:
- Read and write clinical data (orders, visits, observations, vitals, chief complaints, physical exam notes, etc.)
- Enforce request/response schemas
- Provide API key authentication
- Support local and Docker-based development

Main app entrypoint:
- `app/main.py`

## 2. Tech Stack

- Python 3.11+
- FastAPI
- SQLAlchemy (sync ORM usage)
- PyMySQL
- Pydantic v2
- Uvicorn
- Docker / Docker Compose (optional local runtime)

Dependencies are listed in:
- `requirements.txt`

## 3. Repository Map

- `app/main.py`: FastAPI app, middleware, router registration
- `app/api/`: route handlers per domain
- `app/crud/`: business/data-access logic
- `app/models/`: SQLAlchemy models mapping OpenMRS tables
- `app/schemas/`: request/response schemas
- `app/sql/`: raw SQL for complex query paths
- `app/services/`: external integrations (for example OpenMRS search indexing)
- `tests/`: API and behavior tests
- `scripts/`: helper scripts for local/dev/deployment flows
- `docs/`: project documentation

## 4. Prerequisites

Required:
- Python 3.11 or newer
- Access to an OpenMRS/Bahmni MySQL database
- Git

Optional:
- Docker + Docker Compose

Check versions:

```bash
python --version
pip --version
docker --version
docker-compose --version
```

## 5. First-Time Setup (Local)

### Step 1: Create and activate virtual environment

Windows (PowerShell):

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 2: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure environment

Copy template:

Windows:

```powershell
copy env.example .env
```

macOS/Linux:

```bash
cp env.example .env
```

Edit `.env` and set at least:

```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=openmrs
DB_USER=your_db_user
DB_PASSWORD=your_db_password

API_KEYS=omrs_dev_key_1
SECRET_KEY=change-me

HOST=0.0.0.0
PORT=1221
DEBUG=true
```

Optional OpenMRS REST settings (used by system endpoints such as search index rebuild):

```env
OPENMRS_BASE_URL=http://localhost:8080/openmrs
OPENMRS_REST_USERNAME=admin
OPENMRS_REST_PASSWORD=Admin123
OPENMRS_REST_TIMEOUT_SECONDS=10.0
OPENMRS_REST_VERIFY_SSL=true
```

### Step 4: Start the API

Recommended (manual, most reliable):

```bash
uvicorn app.main:app --host 0.0.0.0 --port 1221 --reload
```

Alternative helpers:
- `scripts/start_dev.py`
- `scripts/start_dev.bat`

## 6. Verify It Works

Health check:

```bash
curl http://localhost:1221/health
```

Swagger docs:

- `http://localhost:1221/docs`

Generate an API key (development utility endpoint):

```bash
curl -X POST http://localhost:1221/generate-api-key
```

Authenticated request example:

```bash
curl -H "Authorization: Bearer omrs_dev_key_1" http://localhost:1221/api/v1/orders/
```

## 7. Running with Docker

Use when you want containerized runtime:

```bash
docker-compose up -d
docker-compose logs -f openmrs-bridge
```

Stop:

```bash
docker-compose down
```

For Bahmni network integration, see:
- `docker-compose.bahmni.yml`
- `docs/README_BAHMNI.md`

## 8. Development Workflow

1. Create a feature branch.
2. Implement changes in `api/`, `crud/`, `schemas/`, and `tests/` as needed.
3. Run tests locally.
4. Validate endpoint behavior from `/docs` or curl/Postman.
5. Open PR with:
   - Problem statement
   - What changed
   - Test evidence
   - Known limitations

## 9. How Data Flows Through the App

Typical request path:

1. Route in `app/api/...`
2. Authentication dependency (`app/auth.py`)
3. CRUD function in `app/crud/...`
4. SQLAlchemy model query/update (`app/models/...`) or raw SQL (`app/sql/...`)
5. Response schema in `app/schemas/...`

When adding/changing an endpoint, update all relevant layers together.

## 10. Common Tasks

### Add a new field to an existing endpoint response

1. Update schema in `app/schemas/...`
2. Update CRUD mapper/hydrator in `app/crud/...`
3. If needed, update SQL joins/selects
4. Add/adjust tests in `tests/...`
5. Re-run and verify response via `/docs`

### Add a new endpoint

1. Add schema models
2. Add CRUD method
3. Add API route function
4. Register router in `app/main.py` (if new router)
5. Add tests

## 11. Testing

Run all tests:

```bash
pytest -q
```

Run a single test file:

```bash
pytest -q tests/test_visits_api.py
```

If your environment cannot run all tests (for example missing DB fixtures), run targeted tests and document what you validated manually.

## 12. Troubleshooting

### Error: `No API keys configured`
- Ensure `.env` has `API_KEYS=...`
- Restart the server after changing `.env`

### Error: DB connection failure
- Validate `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- Confirm DB is reachable from your machine/container

### 401 Unauthorized on API calls
- Use header exactly: `Authorization: Bearer <api_key>`
- Confirm key exists in `API_KEYS`

### Endpoint is missing expected fields
- Check schema in `app/schemas`
- Check CRUD mapping in `app/crud`
- Ensure router uses the intended response model

## 13. Practical Conventions for This Codebase

- Keep business logic in `crud`, not in route handlers.
- Keep request/response contracts explicit in `schemas`.
- Prefer small, focused endpoint functions.
- Maintain backward-compatible responses when possible.
- Add tests for changed behavior, especially response shape changes.

## 14. Suggested First Week Onboarding Checklist

1. Run service locally and hit `/health` + `/docs`.
2. Make one small schema + CRUD response change and verify it.
3. Run at least one relevant test file.
4. Trace one full feature from route to DB query and back.
5. Review `docs/SETUP_GUIDE.md` and `docs/README_BAHMNI.md` for deployment context.

Once you complete the checklist, you should be able to implement most API changes independently.
