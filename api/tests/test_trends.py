"""
Test trend endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models import Trend, TrendImage


class TestTrendsListEndpoint:
    """Test trends list endpoint"""

    def test_get_trends_empty(self, client: TestClient, db: Session):
        """Test getting trends from empty database"""
        response = client.get("/api/v1/trends/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_trends_with_data(
        self,
        client: TestClient,
        db: Session,
        sample_trend,
        sample_trend_image
    ):
        """Test getting trends with data"""
        response = client.get("/api/v1/trends/")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) == 1

        # Check trend structure
        trend = data[0]
        expected_fields = [
            "id", "trend_id", "name", "description", "image_hash",
            "image_count", "positive_image_count", "negative_image_count"
        ]

        for field in expected_fields:
            assert field in trend

        assert trend["trend_id"] == sample_trend.trend_id
        assert trend["name"] == sample_trend.name
        assert trend["image_count"] == 1
        assert trend["positive_image_count"] == 1
        assert trend["negative_image_count"] == 0

    def test_get_trends_filter_by_vertical_id(
        self,
        client: TestClient,
        db: Session,
        sample_trend,
        sample_vertical
    ):
        """Test filtering trends by vertical ID"""
        response = client.get(f"/api/v1/trends/?vertical_id={sample_vertical.id}")

        assert response.status_code == 200
        data = response.json()

        assert len(data) >= 1
        # All trends should belong to the specified vertical
        for trend in data:
            # We can't directly check vertical_id in response, but we know our sample trend belongs to sample_vertical
            assert trend["trend_id"] == sample_trend.trend_id

    def test_get_trends_filter_by_vertical_name(
        self,
        client: TestClient,
        db: Session,
        sample_trend,
        sample_vertical
    ):
        """Test filtering trends by vertical name"""
        response = client.get("/api/v1/trends/?vertical_name=Nike")

        assert response.status_code == 200
        data = response.json()

        # Should find trends from verticals with "Nike" in the name
        for trend in data:
            assert trend["trend_id"] == sample_trend.trend_id

    def test_get_trends_filter_by_category(
        self,
        client: TestClient,
        db: Session,
        sample_trend,
        sample_category
    ):
        """Test filtering trends by category"""
        response = client.get(f"/api/v1/trends/?category_id={sample_category.id}")

        assert response.status_code == 200
        data = response.json()

        assert len(data) >= 1

    def test_get_trends_search_by_name(
        self,
        client: TestClient,
        db: Session,
        sample_trend
    ):
        """Test searching trends by name"""
        response = client.get("/api/v1/trends/?query=Athletic")

        assert response.status_code == 200
        data = response.json()

        # Should find trends with "Athletic" in name or description
        assert len(data) >= 1
        found = any("Athletic" in trend["name"] for trend in data)
        assert found

    def test_get_trends_search_by_description(
        self,
        client: TestClient,
        db: Session,
        sample_trend
    ):
        """Test searching trends by description"""
        response = client.get("/api/v1/trends/?query=footwear")

        assert response.status_code == 200
        data = response.json()

        # Should find trends with "footwear" in description
        assert len(data) >= 1

    def test_get_trends_filter_has_images(
        self,
        client: TestClient,
        db: Session,
        sample_trend,
        sample_trend_image,
        sample_vertical
    ):
        """Test filtering trends that have images"""
        # Create a trend without images
        trend_no_images = Trend(
            trend_id="test_no_images",
            vertical_id=sample_vertical.id,
            name="Trend Without Images",
            description="A trend with no images"
        )
        db.add(trend_no_images)
        db.commit()

        # Filter for trends with images
        response = client.get("/api/v1/trends/?has_images=true")

        assert response.status_code == 200
        data = response.json()

        # Should only return trends with images
        for trend in data:
            assert trend["image_count"] > 0

        # Filter for trends without images
        response = client.get("/api/v1/trends/?has_images=false")

        assert response.status_code == 200
        data = response.json()

        # Should only return trends without images
        for trend in data:
            assert trend["image_count"] == 0

    def test_get_trends_filter_by_image_type(
        self,
        client: TestClient,
        db: Session,
        sample_trend,
        sample_trend_image
    ):
        """Test filtering trends by image type"""
        # Create a negative image
        negative_image = TrendImage(
            trend_id=sample_trend.id,
            image_type="negative",
            md5_hash="negative_hash_123",
            description="Negative test image"
        )
        db.add(negative_image)
        db.commit()

        # Filter by positive images
        response = client.get("/api/v1/trends/?image_type=positive")

        assert response.status_code == 200
        data = response.json()

        # Should find trends with positive images
        assert len(data) >= 1

        # Filter by negative images
        response = client.get("/api/v1/trends/?image_type=negative")

        assert response.status_code == 200
        data = response.json()

        # Should find trends with negative images
        assert len(data) >= 1

    def test_get_trends_pagination(
        self,
        client: TestClient,
        db: Session,
        sample_vertical
    ):
        """Test trends pagination"""
        # Create multiple trends
        for i in range(5):
            trend = Trend(
                trend_id=f"test_trend_{i}",
                vertical_id=sample_vertical.id,
                name=f"Test Trend {i}",
                description=f"Description for trend {i}"
            )
            db.add(trend)
        db.commit()

        # Get first page
        response = client.get("/api/v1/trends/?limit=2&offset=0")

        assert response.status_code == 200
        data = response.json()

        assert len(data) == 2

        # Get second page
        response = client.get("/api/v1/trends/?limit=2&offset=2")

        assert response.status_code == 200
        data_page2 = response.json()

        assert len(data_page2) == 2

        # Should be different trends
        page1_ids = {t["id"] for t in data}
        page2_ids = {t["id"] for t in data_page2}
        assert page1_ids.isdisjoint(page2_ids)


class TestTrendByIdEndpoint:
    """Test trend by ID endpoint"""

    def test_get_trend_by_id_success(
        self,
        client: TestClient,
        db: Session,
        sample_trend
    ):
        """Test getting trend by ID successfully"""
        response = client.get(f"/api/v1/trends/{sample_trend.id}")

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == sample_trend.id
        assert data["trend_id"] == sample_trend.trend_id
        assert data["name"] == sample_trend.name
        assert data["description"] == sample_trend.description
        assert data["image_hash"] == sample_trend.image_hash

        # Check required fields
        expected_fields = [
            "id", "trend_id", "name", "description", "image_hash",
            "created_at", "updated_at"
        ]

        for field in expected_fields:
            assert field in data

    def test_get_trend_by_id_with_images(
        self,
        client: TestClient,
        db: Session,
        sample_trend,
        sample_trend_image
    ):
        """Test getting trend with images included"""
        response = client.get(f"/api/v1/trends/{sample_trend.id}?include_images=true")

        assert response.status_code == 200
        data = response.json()

        assert "images" in data
        assert isinstance(data["images"], list)
        assert len(data["images"]) == 1

        image = data["images"][0]
        expected_image_fields = [
            "id", "image_type", "md5_hash", "description",
            "created_at", "updated_at"
        ]

        for field in expected_image_fields:
            assert field in image

        assert image["image_type"] == sample_trend_image.image_type
        assert image["md5_hash"] == sample_trend_image.md5_hash

    def test_get_trend_by_id_not_found(self, client: TestClient, db: Session):
        """Test getting non-existent trend"""
        response = client.get("/api/v1/trends/999999")

        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Trend not found"

    def test_get_trend_by_id_invalid_id(self, client: TestClient, db: Session):
        """Test getting trend with invalid ID"""
        response = client.get("/api/v1/trends/invalid_id")

        assert response.status_code == 422  # Validation error


class TestTrendFullTextSearch:
    """Test trend full-text search endpoint"""

    def test_fulltext_search_success(
        self,
        client: TestClient,
        db: Session,
        sample_trend
    ):
        """Test full-text search functionality"""
        response = client.get("/api/v1/trends/search/fulltext?q=athletic")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        # Should find results (depends on database support for fulltext)

        # Check result structure if any results found
        if len(data) > 0:
            result = data[0]
            expected_fields = ["id", "trend_id", "name", "description"]

            for field in expected_fields:
                assert field in result

    def test_fulltext_search_no_results(
        self,
        client: TestClient,
        db: Session
    ):
        """Test full-text search with no results"""
        response = client.get("/api/v1/trends/search/fulltext?q=nonexistent_term_xyz")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) == 0

    def test_fulltext_search_limit(
        self,
        client: TestClient,
        db: Session,
        sample_vertical
    ):
        """Test full-text search with limit"""
        # Create multiple trends with similar descriptions
        for i in range(15):
            trend = Trend(
                trend_id=f"search_trend_{i}",
                vertical_id=sample_vertical.id,
                name=f"Search Trend {i}",
                description="This is a searchable trend description for testing fulltext search functionality"
            )
            db.add(trend)
        db.commit()

        response = client.get("/api/v1/trends/search/fulltext?q=searchable&limit=5")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) <= 5

    def test_fulltext_search_invalid_limit(self, client: TestClient, db: Session):
        """Test full-text search with invalid limit"""
        # Test limit too high
        response = client.get("/api/v1/trends/search/fulltext?q=test&limit=200")
        assert response.status_code == 422

        # Test limit too low
        response = client.get("/api/v1/trends/search/fulltext?q=test&limit=0")
        assert response.status_code == 422

    def test_fulltext_search_missing_query(self, client: TestClient, db: Session):
        """Test full-text search without query parameter"""
        response = client.get("/api/v1/trends/search/fulltext")

        assert response.status_code == 422  # Missing required parameter