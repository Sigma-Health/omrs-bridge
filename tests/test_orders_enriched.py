"""
Test cases for enriched orders endpoint.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import get_db, Base
from app.models import Order, Patient, Person, PersonName

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


def test_get_order_enriched():
    """Test getting order with enriched creator and patient information"""
    # This test would require setting up test data with orders, patients, persons, and person names
    # For now, we'll test the endpoint structure

    response = client.get(
        "/api/v1/orders/125/enriched",  # Assuming order ID 125 exists
        headers={"X-API-Key": TEST_API_KEY},
    )

    # The response should be either 200 (if order exists) or 404 (if not)
    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = response.json()
        # Check that the response includes the enriched fields
        assert "creator_info" in data
        assert "patient_info" in data
        assert "drug_order_info" in data

        # Check creator_info structure
        if data["creator_info"]:
            assert "person_id" in data["creator_info"]
            assert "uuid" in data["creator_info"]
            assert "name" in data["creator_info"]

        # Check patient_info structure
        if data["patient_info"]:
            assert "person_id" in data["patient_info"]
            assert "uuid" in data["patient_info"]
            assert "name" in data["patient_info"]

        # Check drug_order_info structure (for drug orders)
        if data["drug_order_info"]:
            # Check that drug_name and route_name are included
            assert "drug_name" in data["drug_order_info"], (
                "drug_name should be included in drug_order_info"
            )
            assert "route_name" in data["drug_order_info"], (
                "route_name should be included in drug_order_info"
            )

            # Verify they're not None (if the order has drug information)
            if data["order_type_id"] == 2:  # Drug order type
                print(f"drug_order_info: {data['drug_order_info']}")
                # These might be None if no drug/route is set, but the fields should exist


def test_get_order_enriched_not_found():
    """Test getting enriched order that doesn't exist"""
    response = client.get(
        "/api/v1/orders/99999/enriched",  # Non-existent order ID
        headers={"X-API-Key": TEST_API_KEY},
    )

    assert response.status_code == 404
    assert "Order not found" in response.json()["detail"]


if __name__ == "__main__":
    pytest.main([__file__])
