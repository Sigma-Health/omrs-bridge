# Diagnosis and ICD10 Implementation

## Overview

This document outlines the complete implementation of diagnosis and ICD10 functionality for the OpenMRS Bridge API. The implementation allows you to retrieve diagnoses for visits with their corresponding ICD10 codes, following the same pattern as your existing SQL query.

## Architecture

The implementation follows the established patterns in your codebase:

1. **Models** - Database models for concept reference mapping
2. **Schemas** - Pydantic schemas for API responses  
3. **SQL** - Query functions for retrieving diagnoses with ICD10 codes
4. **CRUD** - Database operations
5. **API** - FastAPI endpoints
6. **Tests** - Comprehensive test coverage

## Files Created/Modified

### New Files Created

1. **`app/models/concept_reference.py`** - Database models for ICD10 mapping
   - `ConceptReferenceSource` - ICD10 source information
   - `ConceptReferenceTerm` - ICD10 codes and terms
   - `ConceptReferenceMap` - Mapping between concepts and ICD10 codes

2. **`app/schemas/diagnosis.py`** - Pydantic schemas for API responses
   - `ICD10Code` - ICD10 code information
   - `DiagnosisConcept` - Diagnosis concept with ICD10 codes
   - `DiagnosisObservation` - Individual diagnosis observation
   - `VisitDiagnoses` - Diagnoses for a specific visit
   - `DiagnosisResponse` - General diagnosis response

3. **`app/sql/diagnosis_sql.py`** - SQL query functions
   - `get_diagnoses_with_icd10_sql()` - Main query for diagnoses with ICD10
   - `get_diagnoses_by_visit_sql()` - Query for specific visit
   - `get_diagnoses_count_sql()` - Count query for pagination

4. **`app/crud/diagnoses.py`** - CRUD operations
   - `DiagnosesCRUD` class with methods for querying diagnoses
   - Support for filtering by visit, patient, encounter, concept
   - ICD10 code enrichment

5. **`app/api/diagnoses.py`** - FastAPI endpoints
   - `GET /api/v1/diagnoses/` - Get all diagnoses with filters
   - `GET /api/v1/diagnoses/visit/{visit_id}` - Get diagnoses by visit
   - `GET /api/v1/diagnoses/patient/{patient_id}` - Get diagnoses by patient
   - `GET /api/v1/diagnoses/encounter/{encounter_id}` - Get diagnoses by encounter

6. **`tests/test_diagnoses_api.py`** - Comprehensive tests
   - Tests for all endpoints
   - Response structure validation
   - Pagination testing
   - Error handling

### Files Modified

1. **`app/models/__init__.py`** - Added concept reference models
2. **`app/schemas/__init__.py`** - Added diagnosis schemas
3. **`app/crud/__init__.py`** - Added diagnoses CRUD
4. **`app/main.py`** - Registered diagnosis router

## API Endpoints

### Get All Diagnoses
```
GET /api/v1/diagnoses/
```

**Query Parameters:**
- `skip` (int, default=0) - Number of records to skip
- `limit` (int, default=100, max=1000) - Number of records to return
- `visit_id` (int, optional) - Filter by visit ID
- `patient_id` (int, optional) - Filter by patient ID
- `encounter_id` (int, optional) - Filter by encounter ID
- `concept_id` (int, optional) - Filter by concept ID
- `has_icd10` (bool, optional) - Filter for diagnoses with ICD10 codes

### Get Diagnoses by Visit
```
GET /api/v1/diagnoses/visit/{visit_id}
```

### Get Diagnoses by Patient
```
GET /api/v1/diagnoses/patient/{patient_id}
```

### Get Diagnoses by Encounter
```
GET /api/v1/diagnoses/encounter/{encounter_id}
```

## Response Structure

### DiagnosisObservation
```json
{
  "obs_id": 284,
  "uuid": "obs-uuid-here",
  "obs_datetime": "2025-08-29T12:42:48",
  "concept": {
    "concept_id": 123,
    "uuid": "concept-uuid",
    "name": "Cervical Pregnancy",
    "short_name": "Cervical Pregnancy",
    "description": "Description here",
    "icd10_codes": [
      {
        "code": "O00.8",
        "name": "Other ectopic pregnancy",
        "version": "2023",
        "description": "ICD10 description"
      }
    ]
  },
  "patient": {
    "patient_id": 87,
    "uuid": "patient-uuid",
    "name": "John Phiri",
    "gender": "M",
    "birthdate": "1990-01-01T00:00:00"
  },
  "encounter": {
    "encounter_id": 456,
    "uuid": "encounter-uuid",
    "encounter_datetime": "2025-08-29T12:42:48",
    "encounter_type": 1,
    "location_id": 1
  },
  "comments": "Additional notes",
  "status": "FINAL",
  "interpretation": "NORMAL"
}
```

### VisitDiagnoses
```json
{
  "visit_id": 123,
  "visit_uuid": "visit-uuid",
  "patient": {
    "patient_id": 87,
    "uuid": "patient-uuid",
    "name": "John Phiri",
    "gender": "M",
    "birthdate": "1990-01-01T00:00:00"
  },
  "diagnoses": [
    // Array of DiagnosisObservation objects
  ],
  "total_count": 5
}
```

## SQL Query Implementation

The implementation is based on your original SQL query:

```sql
SELECT
    o.obs_id,
    p.patient_id,
    pn.given_name,
    pn.family_name,
    cn.name AS diagnosis_name,
    crt.code AS icd10_code,
    e.encounter_datetime
FROM obs o
JOIN encounter e ON o.encounter_id = e.encounter_id
JOIN patient p ON e.patient_id = p.patient_id
JOIN person_name pn ON p.patient_id = pn.person_id AND pn.preferred = 1
JOIN concept c ON o.value_coded = c.concept_id
JOIN concept_name cn ON c.concept_id = cn.concept_id
    AND cn.locale = 'en'
    AND cn.concept_name_type = 'FULLY_SPECIFIED'
LEFT JOIN concept_reference_map crm ON c.concept_id = crm.concept_id
LEFT JOIN concept_reference_term crt ON crm.concept_reference_term_id = crt.concept_reference_term_id
LEFT JOIN concept_reference_source crs ON crt.concept_source_id = crs.concept_source_id
WHERE o.voided = 0
  AND o.value_coded IS NOT NULL
  AND crs.name LIKE '%ICD-10%';
```

## Usage Examples

### Get all diagnoses with ICD10 codes
```bash
curl -H "X-API-Key: your-api-key" \
  "http://localhost:8000/api/v1/diagnoses/?has_icd10=true"
```

### Get diagnoses for a specific visit
```bash
curl -H "X-API-Key: your-api-key" \
  "http://localhost:8000/api/v1/diagnoses/visit/123"
```

### Get diagnoses for a patient
```bash
curl -H "X-API-Key: your-api-key" \
  "http://localhost:8000/api/v1/diagnoses/patient/87"
```

## Testing

Run the tests with:
```bash
pytest tests/test_diagnoses_api.py -v
```

The tests cover:
- All API endpoints
- Response structure validation
- Pagination
- Error handling
- Filtering functionality

## Key Features

1. **ICD10 Code Mapping** - Automatically includes ICD10 codes when available
2. **Flexible Filtering** - Filter by visit, patient, encounter, or concept
3. **Rich Data** - Includes patient, encounter, and concept information
4. **Pagination** - Supports skip/limit for large datasets
5. **Consistent API** - Follows the same patterns as your existing endpoints
6. **Comprehensive Testing** - Full test coverage for all functionality

## Database Structure

The implementation uses these OpenMRS tables:

### Required Tables
- `concept_reference_source` - ICD10 source definitions
- `concept_reference_term` - ICD10 codes and terms  
- `concept_reference_map` - Mappings between concepts and ICD10 codes
- `obs` - Observations (diagnoses)
- `encounter` - Encounters
- `visit` - Visits
- `patient` - Patient information
- `person` - Person details
- `person_name` - Patient names
- `concept` - Diagnosis concepts
- `concept_name` - Concept names

### ICD10 Source Configuration

The system looks for ICD10 sources using:
- `name LIKE '%ICD-10%'` OR `name LIKE '%ICD10%'` OR `hl7_code = 'ICD-10'`

## Next Steps

1. **Verify Database Structure** - Run the setup verification script:
   ```bash
   python scripts/test_diagnosis_setup.py
   ```

2. **Check ICD10 Sources** - Ensure you have ICD10 mappings in your database:
   ```sql
   SELECT * FROM concept_reference_source WHERE name LIKE '%ICD%';
   ```

3. **API Key Setup** - Configure your API keys for authentication

4. **Testing** - Run the tests to verify functionality:
   ```bash
   pytest tests/test_diagnoses_api.py -v
   ```

5. **Integration** - Test with your actual OpenMRS database

## Troubleshooting

### No ICD10 Sources Found
If the verification script shows no ICD10 sources, you may need to:
1. Import ICD10 mappings into `concept_reference_source`
2. Import ICD10 codes into `concept_reference_term`  
3. Create mappings in `concept_reference_map`

### No Diagnosis Observations
If no diagnosis observations are found:
1. Check that observations have `value_coded` values
2. Verify that concepts have proper names in `concept_name`
3. Ensure observations are not voided

The implementation is ready to use and follows all the established patterns in your codebase!
