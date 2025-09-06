"""
Test cases for order types API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from app.main import app
from app.database import get_db, Base
from app.models import OrderType

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


def test_create_order_type():
    """Test creating a new order type"""
    order_type_data = {
        "creator": 1,
        "name": "Test Order Type",
        "description": "A test order type for testing purposes",
        "java_class_name": "org.openmrs.TestOrderType",
    }

    response = client.post(
        "/api/v1/order-types/",
        json=order_type_data,
        headers={"X-API-Key": TEST_API_KEY},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Order Type"
    assert data["description"] == "A test order type for testing purposes"
    assert data["java_class_name"] == "org.openmrs.TestOrderType"
    assert "order_type_id" in data
    assert "uuid" in data
    assert "date_created" in data


def test_get_order_type_by_id():
    """Test getting an order type by ID"""
    # First create an order type
    order_type_data = {
        "creator": 1,
        "name": "Test Order Type 2",
        "description": "Another test order type",
        "java_class_name": "org.openmrs.TestOrderType2",
    }

    create_response = client.post(
        "/api/v1/order-types/",
        json=order_type_data,
        headers={"X-API-Key": TEST_API_KEY},
    )
    order_type_id = create_response.json()["order_type_id"]

    # Then get it by ID
    response = client.get(
        f"/api/v1/order-types/{order_type_id}", headers={"X-API-Key": TEST_API_KEY}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["order_type_id"] == order_type_id
    assert data["name"] == "Test Order Type 2"


def test_get_order_type_by_name():
    """Test getting an order type by name"""
    # First create an order type
    order_type_data = {
        "creator": 1,
        "name": "Unique Order Type",
        "description": "A unique order type",
        "java_class_name": "org.openmrs.UniqueOrderType",
    }

    client.post(
        "/api/v1/order-types/",
        json=order_type_data,
        headers={"X-API-Key": TEST_API_KEY},
    )

    # Then get it by name
    response = client.get(
        "/api/v1/order-types/name/Unique Order Type",
        headers={"X-API-Key": TEST_API_KEY},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Unique Order Type"


def test_list_order_types():
    """Test listing order types"""
    response = client.get("/api/v1/order-types/", headers={"X-API-Key": TEST_API_KEY})

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_list_active_order_types():
    """Test listing active order types"""
    response = client.get(
        "/api/v1/order-types/active", headers={"X-API-Key": TEST_API_KEY}
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_search_order_types():
    """Test searching order types"""
    response = client.get(
        "/api/v1/order-types/search?search_term=Test",
        headers={"X-API-Key": TEST_API_KEY},
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_order_types_by_java_class():
    """Test getting order types by Java class"""
    response = client.get(
        "/api/v1/order-types/java-class/org.openmrs.TestOrderType",
        headers={"X-API-Key": TEST_API_KEY},
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_root_order_types():
    """Test getting root order types"""
    response = client.get(
        "/api/v1/order-types/root", headers={"X-API-Key": TEST_API_KEY}
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_update_order_type_partial():
    """Test partial update of an order type"""
    # First create an order type
    order_type_data = {
        "creator": 1,
        "name": "Update Test Order Type",
        "description": "Original description",
        "java_class_name": "org.openmrs.UpdateTestOrderType",
    }

    create_response = client.post(
        "/api/v1/order-types/",
        json=order_type_data,
        headers={"X-API-Key": TEST_API_KEY},
    )
    order_type_id = create_response.json()["order_type_id"]

    # Then update it
    update_data = {
        "description": "Updated description",
        "java_class_name": "org.openmrs.UpdatedTestOrderType",
    }

    response = client.patch(
        f"/api/v1/order-types/{order_type_id}",
        json=update_data,
        headers={"X-API-Key": TEST_API_KEY},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["order_type_id"] == order_type_id
    assert "updated_fields" in data
    assert data["order_type"]["description"] == "Updated description"
    assert data["order_type"]["java_class_name"] == "org.openmrs.UpdatedTestOrderType"


def test_retire_order_type():
    """Test retiring an order type"""
    # First create an order type
    order_type_data = {
        "creator": 1,
        "name": "Retire Test Order Type",
        "description": "An order type to be retired",
        "java_class_name": "org.openmrs.RetireTestOrderType",
    }

    create_response = client.post(
        "/api/v1/order-types/",
        json=order_type_data,
        headers={"X-API-Key": TEST_API_KEY},
    )
    order_type_id = create_response.json()["order_type_id"]

    # Then retire it
    response = client.post(
        f"/api/v1/order-types/{order_type_id}/retire",
        params={"retired_by": 1, "retire_reason": "Test retirement"},
        headers={"X-API-Key": TEST_API_KEY},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["order_type_id"] == order_type_id
    assert data["retired"] is True
    assert data["retire_reason"] == "Test retirement"


def test_unretire_order_type():
    """Test unretiring an order type"""
    # First create and retire an order type
    order_type_data = {
        "creator": 1,
        "name": "Unretire Test Order Type",
        "description": "An order type to be unretired",
        "java_class_name": "org.openmrs.UnretireTestOrderType",
    }

    create_response = client.post(
        "/api/v1/order-types/",
        json=order_type_data,
        headers={"X-API-Key": TEST_API_KEY},
    )
    order_type_id = create_response.json()["order_type_id"]

    # Retire it first
    client.post(
        f"/api/v1/order-types/{order_type_id}/retire",
        params={"retired_by": 1},
        headers={"X-API-Key": TEST_API_KEY},
    )

    # Then unretire it
    response = client.post(
        f"/api/v1/order-types/{order_type_id}/unretire",
        params={"unretired_by": 1},
        headers={"X-API-Key": TEST_API_KEY},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["order_type_id"] == order_type_id
    assert data["retired"] is False
    assert data["retire_reason"] is None


if __name__ == "__main__":
    pytest.main([__file__])
