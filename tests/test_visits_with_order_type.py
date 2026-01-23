"""
Test cases for visits with order type endpoint.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from app.main import app
from app.database import get_db, Base
from app.models import Visit, Order

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


def test_get_visits_with_order_type():
    """Test getting visits that have orders of a particular order type"""
    # First create a visit
    visit_data = {
        "creator": 1,
        "patient_id": 9,
        "visit_type_id": 4,
        "location_id": 2,
    }

    create_response = client.post(
        "/api/v1/visits/",
        json=visit_data,
        headers={"X-API-Key": TEST_API_KEY},
    )
    visit_id = create_response.json()["visit_id"]

    # Create an order for this visit (this would normally be done through the orders API)
    # For testing purposes, we'll assume the order exists in the database
    # In a real scenario, you'd create the order first

    # Test getting visits with a specific order type
    response = client.get(
        "/api/v1/visits/with-order-type/2",  # Drug Order type
        headers={"X-API-Key": TEST_API_KEY},
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_visits_with_order_type_with_date_filter():
    """Test getting visits with order type and date filter"""
    response = client.get(
        "/api/v1/visits/with-order-type/2?start_date=2024-01-01&end_date=2024-12-31",
        headers={"X-API-Key": TEST_API_KEY},
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_visits_with_order_type_with_patient_filter():
    """Test getting visits with order type and patient filter"""
    response = client.get(
        "/api/v1/visits/with-order-type/2?patient_id=9",
        headers={"X-API-Key": TEST_API_KEY},
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_visits_with_order_type_with_all_filters():
    """Test getting visits with order type and all filters"""
    response = client.get(
        "/api/v1/visits/with-order-type/2?start_date=2024-01-01&end_date=2024-12-31&patient_id=9&skip=0&limit=10",
        headers={"X-API-Key": TEST_API_KEY},
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


if __name__ == "__main__":
    pytest.main([__file__])
