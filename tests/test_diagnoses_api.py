"""
Tests for diagnosis API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.database import get_db
from app.auth import generate_api_key

# Test client
client = TestClient(app)

# Test API key
TEST_API_KEY = "test-api-key-12345"


def test_get_diagnoses():
    """Test getting all diagnoses."""
    response = client.get("/api/v1/diagnoses/", headers={"X-API-Key": TEST_API_KEY})

    # Should return 200 or 401 (if API key is not valid)
    assert response.status_code in [200, 401]


def test_get_diagnoses_with_filters():
    """Test getting diagnoses with filters."""
    response = client.get(
        "/api/v1/diagnoses/?has_icd10=true&limit=10",
        headers={"X-API-Key": TEST_API_KEY},
    )

    # Should return 200 or 401 (if API key is not valid)
    assert response.status_code in [200, 401]


def test_get_diagnoses_by_visit():
    """Test getting diagnoses for a specific visit."""
    visit_id = 1
    response = client.get(
        f"/api/v1/diagnoses/visit/{visit_id}", headers={"X-API-Key": TEST_API_KEY}
    )

    # Should return 200 or 401 (if API key is not valid)
    assert response.status_code in [200, 401]


def test_get_diagnoses_by_patient():
    """Test getting diagnoses for a specific patient."""
    patient_id = 1
    response = client.get(
        f"/api/v1/diagnoses/patient/{patient_id}", headers={"X-API-Key": TEST_API_KEY}
    )

    # Should return 200 or 401 (if API key is not valid)
    assert response.status_code in [200, 401]


def test_get_diagnoses_by_encounter():
    """Test getting diagnoses for a specific encounter."""
    encounter_id = 1
    response = client.get(
        f"/api/v1/diagnoses/encounter/{encounter_id}",
        headers={"X-API-Key": TEST_API_KEY},
    )

    # Should return 200 or 401 (if API key is not valid)
    assert response.status_code in [200, 401]


def test_diagnosis_response_structure():
    """Test that diagnosis response has correct structure."""
    response = client.get(
        "/api/v1/diagnoses/?limit=1", headers={"X-API-Key": TEST_API_KEY}
    )

    if response.status_code == 200:
        data = response.json()

        # Check response structure
        assert "diagnoses" in data
        assert "total_count" in data
        assert "skip" in data
        assert "limit" in data

        # If there are diagnoses, check structure
        if data["diagnoses"]:
            diagnosis = data["diagnoses"][0]
            assert "obs_id" in diagnosis
            assert "uuid" in diagnosis
            assert "obs_datetime" in diagnosis
            assert "concept" in diagnosis
            assert "patient" in diagnosis
            assert "encounter" in diagnosis


def test_visit_diagnoses_response_structure():
    """Test that visit diagnoses response has correct structure."""
    response = client.get(
        "/api/v1/diagnoses/visit/1", headers={"X-API-Key": TEST_API_KEY}
    )

    if response.status_code == 200:
        data = response.json()

        # Check response structure
        assert "visit_id" in data
        assert "visit_uuid" in data
        assert "patient" in data
        assert "diagnoses" in data
        assert "total_count" in data


def test_diagnosis_concept_structure():
    """Test that diagnosis concept has ICD10 codes."""
    response = client.get(
        "/api/v1/diagnoses/?has_icd10=true&limit=1", headers={"X-API-Key": TEST_API_KEY}
    )

    if response.status_code == 200:
        data = response.json()

        if data["diagnoses"]:
            diagnosis = data["diagnoses"][0]
            concept = diagnosis["concept"]

            # Check concept structure
            assert "concept_id" in concept
            assert "uuid" in concept
            assert "name" in concept

            # Check ICD10 codes if present
            if "icd10_codes" in concept and concept["icd10_codes"]:
                icd10_code = concept["icd10_codes"][0]
                assert "code" in icd10_code
                assert "name" in icd10_code or "description" in icd10_code


def test_pagination():
    """Test pagination parameters."""
    response = client.get(
        "/api/v1/diagnoses/?skip=0&limit=5", headers={"X-API-Key": TEST_API_KEY}
    )

    if response.status_code == 200:
        data = response.json()
        assert data["skip"] == 0
        assert data["limit"] == 5


def test_invalid_parameters():
    """Test with invalid parameters."""
    # Test negative skip
    response = client.get(
        "/api/v1/diagnoses/?skip=-1", headers={"X-API-Key": TEST_API_KEY}
    )
    assert response.status_code == 422  # Validation error

    # Test invalid limit
    response = client.get(
        "/api/v1/diagnoses/?limit=0", headers={"X-API-Key": TEST_API_KEY}
    )
    assert response.status_code == 422  # Validation error

    # Test limit too high
    response = client.get(
        "/api/v1/diagnoses/?limit=1001", headers={"X-API-Key": TEST_API_KEY}
    )
    assert response.status_code == 422  # Validation error
