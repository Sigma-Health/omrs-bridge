"""
Test cases for visits API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from app.main import app
from app.database import get_db, Base
from app.models import Visit

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create test database tables
Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# Test API key (you'll need to set this in your environment)
TEST_API_KEY = "test-api-key-123"


def test_create_visit():
    """Test creating a new visit"""
    visit_data = {
        "creator": 1,
        "patient_id": 9,
        "visit_type_id": 4,
        "location_id": 2,
        "indication_concept_id": None,
    }

    response = client.post(
        "/api/v1/visits/", json=visit_data, headers={"X-API-Key": TEST_API_KEY}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["patient_id"] == 9
    assert data["visit_type_id"] == 4
    assert data["location_id"] == 2
    assert "visit_id" in data
    assert "uuid" in data
    assert "date_created" in data


def test_get_visit_by_id():
    """Test getting a visit by ID"""
    # First create a visit
    visit_data = {"creator": 1, "patient_id": 9, "visit_type_id": 4, "location_id": 2}

    create_response = client.post(
        "/api/v1/visits/", json=visit_data, headers={"X-API-Key": TEST_API_KEY}
    )
    visit_id = create_response.json()["visit_id"]

    # Then get it by ID
    response = client.get(
        f"/api/v1/visits/{visit_id}", headers={"X-API-Key": TEST_API_KEY}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["visit_id"] == visit_id
    assert data["patient_id"] == 9


def test_list_visits():
    """Test listing visits"""
    response = client.get("/api/v1/visits/", headers={"X-API-Key": TEST_API_KEY})

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_visits_by_patient():
    """Test getting visits by patient ID"""
    response = client.get(
        "/api/v1/visits/patient/9", headers={"X-API-Key": TEST_API_KEY}
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_update_visit_partial():
    """Test partial update of a visit"""
    # First create a visit
    visit_data = {"creator": 1, "patient_id": 9, "visit_type_id": 4, "location_id": 2}

    create_response = client.post(
        "/api/v1/visits/", json=visit_data, headers={"X-API-Key": TEST_API_KEY}
    )
    visit_id = create_response.json()["visit_id"]

    # Then update it
    update_data = {"location_id": 3, "indication_concept_id": 123}

    response = client.patch(
        f"/api/v1/visits/{visit_id}",
        json=update_data,
        headers={"X-API-Key": TEST_API_KEY},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["visit_id"] == visit_id
    assert "updated_fields" in data
    assert data["visit"]["location_id"] == 3
    assert data["visit"]["indication_concept_id"] == 123


def test_stop_visit():
    """Test stopping a visit"""
    # First create a visit
    visit_data = {"creator": 1, "patient_id": 9, "visit_type_id": 4, "location_id": 2}

    create_response = client.post(
        "/api/v1/visits/", json=visit_data, headers={"X-API-Key": TEST_API_KEY}
    )
    visit_id = create_response.json()["visit_id"]

    # Then stop it
    response = client.post(
        f"/api/v1/visits/{visit_id}/stop",
        params={"stopped_by": 1},
        headers={"X-API-Key": TEST_API_KEY},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["visit_id"] == visit_id
    assert data["date_stopped"] is not None


def test_void_visit():
    """Test voiding a visit"""
    # First create a visit
    visit_data = {"creator": 1, "patient_id": 9, "visit_type_id": 4, "location_id": 2}

    create_response = client.post(
        "/api/v1/visits/", json=visit_data, headers={"X-API-Key": TEST_API_KEY}
    )
    visit_id = create_response.json()["visit_id"]

    # Then void it
    response = client.post(
        f"/api/v1/visits/{visit_id}/void",
        params={"voided_by": 1, "void_reason": "Test voiding"},
        headers={"X-API-Key": TEST_API_KEY},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["visit_id"] == visit_id
    assert data["voided"] is True
    assert data["void_reason"] == "Test voiding"


if __name__ == "__main__":
    pytest.main([__file__])
