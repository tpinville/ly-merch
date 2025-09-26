"""
Test image endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models import TrendImage


class TestImagesListEndpoint:
    """Test images list endpoint"""

    def test_get_images_empty(self, client: TestClient, db: Session):
        """Test getting images from empty database"""
        response = client.get("/api/v1/images/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_images_with_data(
        self,
        client: TestClient,
        db: Session,
        sample_trend_image
    ):
        """Test getting images with data"""
        response = client.get("/api/v1/images/")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) == 1

        # Check image structure
        image = data[0]
        expected_fields = [
            "id", "image_type", "md5_hash", "description",
            "created_at", "updated_at"
        ]

        for field in expected_fields:
            assert field in image

        assert image["image_type"] == sample_trend_image.image_type
        assert image["md5_hash"] == sample_trend_image.md5_hash
        assert image["description"] == sample_trend_image.description

    def test_get_images_filter_by_trend_id(
        self,
        client: TestClient,
        db: Session,
        sample_trend,
        sample_trend_image
    ):
        """Test filtering images by trend ID"""
        # Create another trend with images
        from app.models import Trend, Vertical, Category

        category2 = Category(name="boots", description="Boot category")
        db.add(category2)
        db.commit()

        vertical2 = Vertical(
            vertical_id="boots:test",
            category_id=category2.id,
            name="Test Boots Vertical",
            geo_zone="US"
        )
        db.add(vertical2)
        db.commit()

        trend2 = Trend(
            trend_id="test_trend_2",
            vertical_id=vertical2.id,
            name="Another Trend",
            description="Another trend for testing"
        )
        db.add(trend2)
        db.commit()

        image2 = TrendImage(
            trend_id=trend2.id,
            image_type="negative",
            md5_hash="another_hash_456",
            description="Another test image"
        )
        db.add(image2)
        db.commit()

        # Filter by first trend
        response = client.get(f"/api/v1/images/?trend_id={sample_trend.id}")

        assert response.status_code == 200
        data = response.json()

        assert len(data) == 1
        assert data[0]["md5_hash"] == sample_trend_image.md5_hash

        # Filter by second trend
        response = client.get(f"/api/v1/images/?trend_id={trend2.id}")

        assert response.status_code == 200
        data = response.json()

        assert len(data) == 1
        assert data[0]["md5_hash"] == "another_hash_456"

    def test_get_images_filter_by_type(
        self,
        client: TestClient,
        db: Session,
        sample_trend,
        sample_trend_image
    ):
        """Test filtering images by type"""
        # Create images of different types
        negative_image = TrendImage(
            trend_id=sample_trend.id,
            image_type="negative",
            md5_hash="negative_hash_789",
            description="Negative test image"
        )
        db.add(negative_image)
        db.commit()

        # Filter by positive type
        response = client.get("/api/v1/images/?image_type=positive")

        assert response.status_code == 200
        data = response.json()

        assert len(data) == 1
        assert data[0]["image_type"] == "positive"
        assert data[0]["md5_hash"] == sample_trend_image.md5_hash

        # Filter by negative type
        response = client.get("/api/v1/images/?image_type=negative")

        assert response.status_code == 200
        data = response.json()

        assert len(data) == 1
        assert data[0]["image_type"] == "negative"
        assert data[0]["md5_hash"] == "negative_hash_789"

    def test_get_images_combined_filters(
        self,
        client: TestClient,
        db: Session,
        sample_trend,
        sample_trend_image
    ):
        """Test combining trend_id and image_type filters"""
        # Create another image for the same trend
        another_image = TrendImage(
            trend_id=sample_trend.id,
            image_type="negative",
            md5_hash="another_negative_hash",
            description="Another negative image"
        )
        db.add(another_image)
        db.commit()

        # Filter by trend_id and image_type
        response = client.get(
            f"/api/v1/images/?trend_id={sample_trend.id}&image_type=positive"
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data) == 1
        assert data[0]["image_type"] == "positive"
        assert data[0]["md5_hash"] == sample_trend_image.md5_hash

    def test_get_images_pagination(
        self,
        client: TestClient,
        db: Session,
        sample_trend
    ):
        """Test images pagination"""
        # Create multiple images
        for i in range(5):
            image = TrendImage(
                trend_id=sample_trend.id,
                image_type="positive",
                md5_hash=f"hash_{i}",
                description=f"Test image {i}"
            )
            db.add(image)
        db.commit()

        # Get first page
        response = client.get("/api/v1/images/?limit=2&offset=0")

        assert response.status_code == 200
        data = response.json()

        assert len(data) == 2

        # Get second page
        response = client.get("/api/v1/images/?limit=2&offset=2")

        assert response.status_code == 200
        data_page2 = response.json()

        assert len(data_page2) == 2

        # Should be different images
        page1_hashes = {img["md5_hash"] for img in data}
        page2_hashes = {img["md5_hash"] for img in data_page2}
        assert page1_hashes.isdisjoint(page2_hashes)

    def test_get_images_invalid_filters(self, client: TestClient, db: Session):
        """Test images with invalid filter values"""
        # Test invalid trend_id
        response = client.get("/api/v1/images/?trend_id=invalid")
        assert response.status_code == 422

        # Test invalid limit
        response = client.get("/api/v1/images/?limit=0")
        assert response.status_code == 422

        # Test invalid offset
        response = client.get("/api/v1/images/?offset=-1")
        assert response.status_code == 422


class TestImageByIdEndpoint:
    """Test image by ID endpoint"""

    def test_get_image_by_id_success(
        self,
        client: TestClient,
        db: Session,
        sample_trend_image
    ):
        """Test getting image by ID successfully"""
        response = client.get(f"/api/v1/images/{sample_trend_image.id}")

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == sample_trend_image.id
        assert data["image_type"] == sample_trend_image.image_type
        assert data["md5_hash"] == sample_trend_image.md5_hash
        assert data["description"] == sample_trend_image.description

        # Check all fields are present
        expected_fields = [
            "id", "image_type", "md5_hash", "description",
            "created_at", "updated_at"
        ]

        for field in expected_fields:
            assert field in data

    def test_get_image_by_id_not_found(self, client: TestClient, db: Session):
        """Test getting non-existent image"""
        response = client.get("/api/v1/images/999999")

        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Image not found"

    def test_get_image_by_id_invalid_id(self, client: TestClient, db: Session):
        """Test getting image with invalid ID"""
        response = client.get("/api/v1/images/invalid_id")

        assert response.status_code == 422  # Validation error


class TestImageStatsEndpoint:
    """Test image statistics endpoint"""

    def test_get_image_stats_empty(self, client: TestClient, db: Session):
        """Test image stats with empty database"""
        response = client.get("/api/v1/images/stats/summary")

        assert response.status_code == 200
        data = response.json()

        assert data["total_images"] == 0
        assert isinstance(data["by_type"], dict)
        assert len(data["by_type"]) == 0

    def test_get_image_stats_with_data(
        self,
        client: TestClient,
        db: Session,
        sample_trend,
        sample_trend_image
    ):
        """Test image stats with data"""
        # Create additional images of different types
        negative_image = TrendImage(
            trend_id=sample_trend.id,
            image_type="negative",
            md5_hash="negative_stats_hash",
            description="Negative image for stats"
        )
        db.add(negative_image)

        another_positive = TrendImage(
            trend_id=sample_trend.id,
            image_type="positive",
            md5_hash="another_positive_hash",
            description="Another positive image"
        )
        db.add(another_positive)
        db.commit()

        response = client.get("/api/v1/images/stats/summary")

        assert response.status_code == 200
        data = response.json()

        assert data["total_images"] == 3

        # Check type distribution
        assert "positive" in data["by_type"]
        assert "negative" in data["by_type"]
        assert data["by_type"]["positive"] == 2
        assert data["by_type"]["negative"] == 1

    def test_get_image_stats_multiple_types(
        self,
        client: TestClient,
        db: Session,
        sample_trend
    ):
        """Test image stats with various image types"""
        # Create images of different types
        image_types = ["positive", "negative", "positive", "negative", "positive"]
        for i, img_type in enumerate(image_types):
            image = TrendImage(
                trend_id=sample_trend.id,
                image_type=img_type,
                md5_hash=f"stats_hash_{i}",
                description=f"Stats image {i}"
            )
            db.add(image)
        db.commit()

        response = client.get("/api/v1/images/stats/summary")

        assert response.status_code == 200
        data = response.json()

        assert data["total_images"] == 5
        assert data["by_type"]["positive"] == 3
        assert data["by_type"]["negative"] == 2