"""
Test category endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TestCategoriesEndpoint:
    """Test categories list endpoint"""

    def test_get_categories_empty(self, client: TestClient, db: Session):
        """Test getting categories from empty database"""
        response = client.get("/api/v1/categories/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_categories_with_data(
        self,
        client: TestClient,
        db: Session,
        multiple_categories
    ):
        """Test getting categories with data"""
        response = client.get("/api/v1/categories/")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) == len(multiple_categories)

        # Check first category structure
        category = data[0]
        expected_fields = [
            "id", "name", "description", "created_at",
            "updated_at", "vertical_count"
        ]

        for field in expected_fields:
            assert field in category

        # Categories should be ordered by name
        category_names = [cat["name"] for cat in data]
        assert category_names == sorted(category_names)

    def test_get_categories_with_vertical_count(
        self,
        client: TestClient,
        db: Session,
        sample_category,
        sample_vertical
    ):
        """Test that categories include correct vertical counts"""
        response = client.get("/api/v1/categories/")

        assert response.status_code == 200
        data = response.json()

        assert len(data) == 1
        category = data[0]

        assert category["id"] == sample_category.id
        assert category["name"] == sample_category.name
        assert category["vertical_count"] == 1

    def test_get_categories_search(
        self,
        client: TestClient,
        db: Session,
        multiple_categories
    ):
        """Test categories search functionality"""
        # Search for 'sneakers'
        response = client.get("/api/v1/categories/?query=sneakers")

        assert response.status_code == 200
        data = response.json()

        # Should find only the sneakers category
        sneakers_categories = [cat for cat in data if "sneakers" in cat["name"]]
        assert len(sneakers_categories) >= 1

        # All returned categories should match the search
        for category in data:
            assert "sneakers" in category["name"].lower()

    def test_get_categories_pagination(
        self,
        client: TestClient,
        db: Session,
        multiple_categories
    ):
        """Test categories pagination"""
        # Get first page with limit 1
        response = client.get("/api/v1/categories/?limit=1&offset=0")

        assert response.status_code == 200
        data = response.json()

        assert len(data) == 1

        # Get second page
        response = client.get("/api/v1/categories/?limit=1&offset=1")

        assert response.status_code == 200
        data_page2 = response.json()

        assert len(data_page2) == 1

        # Should be different categories
        assert data[0]["id"] != data_page2[0]["id"]

    def test_get_categories_limit_validation(self, client: TestClient, db: Session):
        """Test categories limit validation"""
        # Test limit too high
        response = client.get("/api/v1/categories/?limit=2000")

        assert response.status_code == 422  # Validation error

        # Test limit too low
        response = client.get("/api/v1/categories/?limit=0")

        assert response.status_code == 422  # Validation error

    def test_get_categories_offset_validation(self, client: TestClient, db: Session):
        """Test categories offset validation"""
        # Test negative offset
        response = client.get("/api/v1/categories/?offset=-1")

        assert response.status_code == 422  # Validation error


class TestCategoryByIdEndpoint:
    """Test category by ID endpoint"""

    def test_get_category_by_id_success(
        self,
        client: TestClient,
        db: Session,
        sample_category,
        sample_vertical
    ):
        """Test getting category by ID successfully"""
        response = client.get(f"/api/v1/categories/{sample_category.id}")

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == sample_category.id
        assert data["name"] == sample_category.name
        assert data["description"] == sample_category.description
        assert data["vertical_count"] == 1

        # Check datetime fields are present
        assert "created_at" in data
        assert "updated_at" in data

    def test_get_category_by_id_not_found(self, client: TestClient, db: Session):
        """Test getting non-existent category"""
        response = client.get("/api/v1/categories/999999")

        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Category not found"

    def test_get_category_by_id_invalid_id(self, client: TestClient, db: Session):
        """Test getting category with invalid ID"""
        response = client.get("/api/v1/categories/invalid_id")

        assert response.status_code == 422  # Validation error

    def test_get_category_zero_vertical_count(
        self,
        client: TestClient,
        db: Session,
        sample_category
    ):
        """Test category with no verticals has zero count"""
        response = client.get(f"/api/v1/categories/{sample_category.id}")

        assert response.status_code == 200
        data = response.json()

        assert data["vertical_count"] == 0