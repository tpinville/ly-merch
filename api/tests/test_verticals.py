"""
Test vertical endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models import Vertical


class TestVerticalsListEndpoint:
    """Test verticals list endpoint"""

    def test_get_verticals_empty(self, client: TestClient, db: Session):
        """Test getting verticals from empty database"""
        response = client.get("/api/v1/verticals/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_verticals_with_data(
        self,
        client: TestClient,
        db: Session,
        sample_vertical,
        sample_category
    ):
        """Test getting verticals with data"""
        response = client.get("/api/v1/verticals/")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) == 1

        # Check vertical structure
        vertical = data[0]
        expected_fields = [
            "id", "vertical_id", "category_id", "category_name",
            "name", "geo_zone", "trend_count"
        ]

        for field in expected_fields:
            assert field in vertical

        assert vertical["vertical_id"] == sample_vertical.vertical_id
        assert vertical["name"] == sample_vertical.name
        assert vertical["geo_zone"] == sample_vertical.geo_zone
        assert vertical["category_name"] == sample_category.name

    def test_get_verticals_filter_by_geo_zone(
        self,
        client: TestClient,
        db: Session,
        sample_category
    ):
        """Test filtering verticals by geo zone"""
        # Create verticals with different geo zones
        vertical_us = Vertical(
            vertical_id="test:us",
            category_id=sample_category.id,
            name="US Vertical",
            geo_zone="US"
        )
        vertical_eu = Vertical(
            vertical_id="test:eu",
            category_id=sample_category.id,
            name="EU Vertical",
            geo_zone="EU"
        )

        db.add(vertical_us)
        db.add(vertical_eu)
        db.commit()

        # Filter by US geo zone
        response = client.get("/api/v1/verticals/?geo_zone=US")

        assert response.status_code == 200
        data = response.json()

        assert len(data) == 1
        assert data[0]["geo_zone"] == "US"
        assert data[0]["name"] == "US Vertical"

    def test_get_verticals_filter_by_category_id(
        self,
        client: TestClient,
        db: Session,
        sample_vertical,
        sample_category,
        multiple_categories
    ):
        """Test filtering verticals by category ID"""
        response = client.get(f"/api/v1/verticals/?category_id={sample_category.id}")

        assert response.status_code == 200
        data = response.json()

        # All verticals should belong to the specified category
        for vertical in data:
            assert vertical["category_id"] == sample_category.id

    def test_get_verticals_filter_by_category_name(
        self,
        client: TestClient,
        db: Session,
        sample_vertical,
        sample_category
    ):
        """Test filtering verticals by category name"""
        response = client.get(f"/api/v1/verticals/?category_name={sample_category.name}")

        assert response.status_code == 200
        data = response.json()

        # All verticals should belong to categories with matching name
        for vertical in data:
            assert sample_category.name in vertical["category_name"]

    def test_get_verticals_search_by_name(
        self,
        client: TestClient,
        db: Session,
        sample_vertical
    ):
        """Test searching verticals by name"""
        response = client.get(f"/api/v1/verticals/?query=Nike")

        assert response.status_code == 200
        data = response.json()

        # All verticals should contain the search term in name
        for vertical in data:
            assert "nike" in vertical["name"].lower()

    def test_get_verticals_pagination(
        self,
        client: TestClient,
        db: Session,
        sample_category
    ):
        """Test verticals pagination"""
        # Create multiple verticals
        for i in range(5):
            vertical = Vertical(
                vertical_id=f"test:vertical_{i}",
                category_id=sample_category.id,
                name=f"Test Vertical {i}",
                geo_zone="US"
            )
            db.add(vertical)
        db.commit()

        # Get first page
        response = client.get("/api/v1/verticals/?limit=2&offset=0")

        assert response.status_code == 200
        data = response.json()

        assert len(data) == 2

        # Get second page
        response = client.get("/api/v1/verticals/?limit=2&offset=2")

        assert response.status_code == 200
        data_page2 = response.json()

        assert len(data_page2) == 2

        # Should be different verticals
        page1_ids = {v["id"] for v in data}
        page2_ids = {v["id"] for v in data_page2}
        assert page1_ids.isdisjoint(page2_ids)

    def test_get_verticals_with_trend_count(
        self,
        client: TestClient,
        db: Session,
        sample_vertical,
        sample_trend
    ):
        """Test that verticals include correct trend counts"""
        response = client.get("/api/v1/verticals/")

        assert response.status_code == 200
        data = response.json()

        assert len(data) == 1
        vertical = data[0]

        assert vertical["trend_count"] == 1


class TestVerticalByIdEndpoint:
    """Test vertical by ID endpoint"""

    def test_get_vertical_by_id_success(
        self,
        client: TestClient,
        db: Session,
        sample_vertical,
        sample_category
    ):
        """Test getting vertical by ID successfully"""
        response = client.get(f"/api/v1/verticals/{sample_vertical.id}")

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == sample_vertical.id
        assert data["vertical_id"] == sample_vertical.vertical_id
        assert data["name"] == sample_vertical.name
        assert data["geo_zone"] == sample_vertical.geo_zone
        assert data["category_name"] == sample_category.name

        # Check all fields are present
        expected_fields = [
            "id", "vertical_id", "category_id", "category_name",
            "category_description", "name", "geo_zone",
            "created_at", "updated_at", "trend_count"
        ]

        for field in expected_fields:
            assert field in data

    def test_get_vertical_by_id_with_trends(
        self,
        client: TestClient,
        db: Session,
        sample_vertical,
        sample_trend,
        sample_trend_image
    ):
        """Test getting vertical with trends included"""
        response = client.get(f"/api/v1/verticals/{sample_vertical.id}?include_trends=true")

        assert response.status_code == 200
        data = response.json()

        assert "trends" in data
        assert isinstance(data["trends"], list)
        assert len(data["trends"]) == 1

        trend = data["trends"][0]
        expected_trend_fields = [
            "id", "trend_id", "name", "description",
            "image_hash", "image_count", "positive_image_count",
            "negative_image_count"
        ]

        for field in expected_trend_fields:
            assert field in trend

        assert trend["trend_id"] == sample_trend.trend_id
        assert trend["name"] == sample_trend.name
        assert trend["image_count"] == 1
        assert trend["positive_image_count"] == 1

    def test_get_vertical_by_id_not_found(self, client: TestClient, db: Session):
        """Test getting non-existent vertical"""
        response = client.get("/api/v1/verticals/999999")

        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Vertical not found"

    def test_get_vertical_by_id_invalid_id(self, client: TestClient, db: Session):
        """Test getting vertical with invalid ID"""
        response = client.get("/api/v1/verticals/invalid_id")

        assert response.status_code == 422  # Validation error


class TestGeoZonesEndpoint:
    """Test geo zones endpoint"""

    def test_get_geo_zones_empty(self, client: TestClient, db: Session):
        """Test getting geo zones from empty database"""
        response = client.get("/api/v1/verticals/search/geo-zones")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_geo_zones_with_data(
        self,
        client: TestClient,
        db: Session,
        sample_category
    ):
        """Test getting geo zones with data"""
        # Create verticals with different geo zones
        geo_zones = ["US", "EU", "ASIA", "US"]  # US appears twice
        for i, zone in enumerate(geo_zones):
            vertical = Vertical(
                vertical_id=f"test:{zone.lower()}_{i}",
                category_id=sample_category.id,
                name=f"Vertical {zone} {i}",
                geo_zone=zone
            )
            db.add(vertical)
        db.commit()

        response = client.get("/api/v1/verticals/search/geo-zones")

        assert response.status_code == 200
        data = response.json()

        # Should return unique geo zones
        assert isinstance(data, list)
        assert len(set(data)) == 3  # US, EU, ASIA (unique)
        assert "US" in data
        assert "EU" in data
        assert "ASIA" in data