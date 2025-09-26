"""
Test health and statistics endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TestHealthEndpoint:
    """Test health check endpoint"""

    def test_health_endpoint_success(self, client: TestClient):
        """Test health endpoint returns success"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "ok"
        assert data["api_version"] == "1.0.0"
        assert "database" in data

    def test_health_endpoint_database_status(self, client: TestClient, db: Session):
        """Test health endpoint includes database status"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        # Database health should be included
        assert "database" in data
        db_status = data["database"]
        assert "status" in db_status


class TestRootEndpoint:
    """Test root endpoint"""

    def test_root_endpoint(self, client: TestClient):
        """Test root endpoint returns API information"""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()

        assert data["message"] == "Fashion Trends API"
        assert data["version"] == "1.0.0"
        assert data["docs"] == "/docs"
        assert "endpoints" in data

        endpoints = data["endpoints"]
        expected_endpoints = [
            "categories", "verticals", "trends",
            "images", "products", "health"
        ]

        for endpoint in expected_endpoints:
            assert endpoint in endpoints


class TestStatsEndpoint:
    """Test statistics endpoint"""

    def test_empty_stats(self, client: TestClient, db: Session):
        """Test stats endpoint with empty database"""
        response = client.get("/api/v1/stats")

        assert response.status_code == 200
        data = response.json()

        # Should have all count fields
        expected_fields = [
            "total_categories", "total_verticals", "total_trends",
            "total_images", "total_products", "categories",
            "geo_zones", "image_types"
        ]

        for field in expected_fields:
            assert field in data

        # All counts should be zero for empty database
        assert data["total_categories"] == 0
        assert data["total_verticals"] == 0
        assert data["total_trends"] == 0
        assert data["total_images"] == 0
        assert data["total_products"] == 0

    def test_stats_with_data(
        self,
        client: TestClient,
        db: Session,
        sample_category,
        sample_vertical,
        sample_trend,
        sample_trend_image,
        sample_product
    ):
        """Test stats endpoint with sample data"""
        response = client.get("/api/v1/stats")

        assert response.status_code == 200
        data = response.json()

        # Should reflect the sample data
        assert data["total_categories"] == 1
        assert data["total_verticals"] == 1
        assert data["total_trends"] == 1
        assert data["total_images"] == 1
        assert data["total_products"] == 1

        # Category distribution
        assert sample_category.name in data["categories"]
        assert data["categories"][sample_category.name] == 1

        # Geo zone distribution
        assert sample_vertical.geo_zone in data["geo_zones"]
        assert data["geo_zones"][sample_vertical.geo_zone] == 1

        # Image type distribution
        assert sample_trend_image.image_type in data["image_types"]
        assert data["image_types"][sample_trend_image.image_type] == 1

    def test_stats_multiple_categories(
        self,
        client: TestClient,
        db: Session,
        multiple_categories
    ):
        """Test stats endpoint with multiple categories"""
        response = client.get("/api/v1/stats")

        assert response.status_code == 200
        data = response.json()

        assert data["total_categories"] == len(multiple_categories)

        # Check that all categories are included
        for category in multiple_categories:
            assert category.name in data["categories"]