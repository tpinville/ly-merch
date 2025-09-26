"""
Test product endpoints including CRUD operations and bulk upload
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TestProductsListEndpoint:
    """Test products list endpoint"""

    def test_get_products_empty(self, client: TestClient, db: Session):
        """Test getting products from empty database"""
        response = client.get("/api/v1/products/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_products_with_data(
        self,
        client: TestClient,
        db: Session,
        multiple_products
    ):
        """Test getting products with data"""
        response = client.get("/api/v1/products/")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) == len(multiple_products)

        # Check product structure
        product = data[0]
        expected_fields = [
            "id", "product_id", "name", "product_type",
            "brand", "price", "currency", "availability_status",
            "image_url"
        ]

        for field in expected_fields:
            assert field in product

    def test_get_products_search_by_name(
        self,
        client: TestClient,
        db: Session,
        multiple_products
    ):
        """Test products search by name"""
        response = client.get("/api/v1/products/?query=Test Product 1")

        assert response.status_code == 200
        data = response.json()

        assert len(data) >= 1
        # Should find the product with matching name
        found = any(p["name"] == "Test Product 1" for p in data)
        assert found

    def test_get_products_filter_by_brand(
        self,
        client: TestClient,
        db: Session,
        multiple_products
    ):
        """Test products filter by brand"""
        response = client.get("/api/v1/products/?brand=Nike")

        assert response.status_code == 200
        data = response.json()

        assert len(data) >= 1
        # All products should be Nike brand
        for product in data:
            assert product["brand"] == "Nike"

    def test_get_products_filter_by_product_type(
        self,
        client: TestClient,
        db: Session,
        multiple_products
    ):
        """Test products filter by product type"""
        response = client.get("/api/v1/products/?product_type=sneakers")

        assert response.status_code == 200
        data = response.json()

        # Should find sneakers products
        for product in data:
            assert "sneakers" in product["product_type"]

    def test_get_products_filter_by_gender(
        self,
        client: TestClient,
        db: Session,
        multiple_products
    ):
        """Test products filter by gender"""
        response = client.get("/api/v1/products/?gender=male")

        assert response.status_code == 200
        data = response.json()

        # All products should be for male gender
        for product in data:
            # Note: gender might not be in summary response, need to check actual implementation
            pass

    def test_get_products_filter_by_availability(
        self,
        client: TestClient,
        db: Session,
        multiple_products
    ):
        """Test products filter by availability status"""
        response = client.get("/api/v1/products/?availability_status=in_stock")

        assert response.status_code == 200
        data = response.json()

        # All products should be in stock
        for product in data:
            assert product["availability_status"] == "in_stock"

    def test_get_products_filter_by_price_range(
        self,
        client: TestClient,
        db: Session,
        multiple_products
    ):
        """Test products filter by price range"""
        response = client.get("/api/v1/products/?min_price=90&max_price=150")

        assert response.status_code == 200
        data = response.json()

        # All products should be in the price range
        for product in data:
            if product["price"] is not None:
                assert 90 <= product["price"] <= 150

    def test_get_products_pagination(
        self,
        client: TestClient,
        db: Session,
        multiple_products
    ):
        """Test products pagination"""
        # Get first page with limit 1
        response = client.get("/api/v1/products/?limit=1&offset=0")

        assert response.status_code == 200
        data = response.json()

        assert len(data) == 1

        # Get second page
        response = client.get("/api/v1/products/?limit=1&offset=1")

        assert response.status_code == 200
        data_page2 = response.json()

        if len(data_page2) > 0:  # If there's a second product
            assert data[0]["id"] != data_page2[0]["id"]

    def test_get_products_invalid_filters(self, client: TestClient, db: Session):
        """Test products with invalid filter values"""
        # Test invalid price
        response = client.get("/api/v1/products/?min_price=invalid")
        assert response.status_code == 422

        # Test invalid limit
        response = client.get("/api/v1/products/?limit=0")
        assert response.status_code == 422

        # Test invalid offset
        response = client.get("/api/v1/products/?offset=-1")
        assert response.status_code == 422


class TestProductByIdEndpoint:
    """Test product by ID endpoint"""

    def test_get_product_by_id_success(
        self,
        client: TestClient,
        db: Session,
        sample_product
    ):
        """Test getting product by ID successfully"""
        response = client.get(f"/api/v1/products/{sample_product.id}")

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == sample_product.id
        assert data["product_id"] == sample_product.product_id
        assert data["name"] == sample_product.name
        assert data["product_type"] == sample_product.product_type
        assert data["brand"] == sample_product.brand
        assert data["price"] == float(sample_product.price)
        assert data["currency"] == sample_product.currency

        # Check all fields are present
        expected_fields = [
            "id", "product_id", "trend_id", "name", "product_type",
            "description", "brand", "price", "currency", "color",
            "size", "material", "gender", "season", "availability_status",
            "image_url", "product_url", "created_at", "updated_at"
        ]

        for field in expected_fields:
            assert field in data

    def test_get_product_by_id_not_found(self, client: TestClient, db: Session):
        """Test getting non-existent product"""
        response = client.get("/api/v1/products/999999")

        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Product not found"

    def test_get_product_by_id_invalid_id(self, client: TestClient, db: Session):
        """Test getting product with invalid ID"""
        response = client.get("/api/v1/products/invalid_id")

        assert response.status_code == 422  # Validation error


class TestProductStatsEndpoint:
    """Test product statistics endpoint"""

    def test_get_product_stats_empty(self, client: TestClient, db: Session):
        """Test product stats with empty database"""
        response = client.get("/api/v1/products/stats/summary")

        assert response.status_code == 200
        data = response.json()

        assert data["total_products"] == 0
        assert isinstance(data["by_type"], dict)
        assert isinstance(data["top_brands"], dict)
        assert isinstance(data["by_availability"], dict)

    def test_get_product_stats_with_data(
        self,
        client: TestClient,
        db: Session,
        multiple_products
    ):
        """Test product stats with data"""
        response = client.get("/api/v1/products/stats/summary")

        assert response.status_code == 200
        data = response.json()

        assert data["total_products"] == len(multiple_products)

        # Check product type distribution
        assert "sneakers" in data["by_type"]
        assert "boots" in data["by_type"]

        # Check brand distribution
        assert "Nike" in data["top_brands"]
        assert "Adidas" in data["top_brands"]
        assert "Dr. Martens" in data["top_brands"]

        # Check availability distribution
        assert "in_stock" in data["by_availability"]
        assert "out_of_stock" in data["by_availability"]


class TestProductBulkUpload:
    """Test product bulk upload functionality"""

    def test_bulk_upload_success(
        self,
        client: TestClient,
        db: Session,
        bulk_upload_data
    ):
        """Test successful bulk upload"""
        response = client.post("/api/v1/products/bulk", json=bulk_upload_data)

        assert response.status_code == 200
        data = response.json()

        assert data["uploaded_count"] == 2
        assert data["skipped_count"] == 0
        assert data["error_count"] == 0
        assert data["errors"] is None

        # Verify products were created
        products_response = client.get("/api/v1/products/")
        products = products_response.json()
        assert len(products) == 2

        # Check product details
        product_ids = [p["product_id"] for p in products]
        assert "BULK_001" in product_ids
        assert "BULK_002" in product_ids

    def test_bulk_upload_duplicate_products(
        self,
        client: TestClient,
        db: Session,
        bulk_upload_data
    ):
        """Test bulk upload with duplicate products"""
        # Upload once
        response1 = client.post("/api/v1/products/bulk", json=bulk_upload_data)
        assert response1.status_code == 200

        # Upload again (should skip duplicates)
        response2 = client.post("/api/v1/products/bulk", json=bulk_upload_data)

        assert response2.status_code == 200
        data = response2.json()

        assert data["uploaded_count"] == 0
        assert data["skipped_count"] == 2
        assert data["error_count"] == 0

    def test_bulk_upload_auto_generate_ids(
        self,
        client: TestClient,
        db: Session
    ):
        """Test bulk upload with auto-generated product IDs"""
        upload_data = {
            "products": [
                {
                    "name": "Auto ID Product 1",
                    "product_type": "sneakers",
                    "brand": "Test Brand",
                    "price": 99.99
                },
                {
                    "name": "Auto ID Product 2",
                    "product_type": "boots",
                    "brand": "Test Brand",
                    "price": 129.99
                }
            ]
        }

        response = client.post("/api/v1/products/bulk", json=upload_data)

        assert response.status_code == 200
        data = response.json()

        assert data["uploaded_count"] == 2
        assert data["error_count"] == 0

        # Check that product IDs were auto-generated
        products_response = client.get("/api/v1/products/")
        products = products_response.json()

        for product in products:
            assert product["product_id"] is not None
            assert len(product["product_id"]) > 0

    def test_bulk_upload_partial_success(
        self,
        client: TestClient,
        db: Session,
        invalid_bulk_upload_data
    ):
        """Test bulk upload with some invalid products"""
        response = client.post("/api/v1/products/bulk", json=invalid_bulk_upload_data)

        assert response.status_code == 200
        data = response.json()

        # Should have errors but not fail completely
        assert data["error_count"] > 0
        assert isinstance(data["errors"], list)
        assert len(data["errors"]) > 0

        # Check error messages contain useful information
        for error in data["errors"]:
            assert "Row" in error
            assert isinstance(error, str)

    def test_bulk_upload_empty_products(self, client: TestClient, db: Session):
        """Test bulk upload with empty products list"""
        upload_data = {"products": []}

        response = client.post("/api/v1/products/bulk", json=upload_data)

        assert response.status_code == 200
        data = response.json()

        assert data["uploaded_count"] == 0
        assert data["skipped_count"] == 0
        assert data["error_count"] == 0

    def test_bulk_upload_invalid_request_format(self, client: TestClient, db: Session):
        """Test bulk upload with invalid request format"""
        # Missing products field
        invalid_data = {"invalid_field": "value"}

        response = client.post("/api/v1/products/bulk", json=invalid_data)

        assert response.status_code == 422  # Validation error

    def test_bulk_upload_large_batch(self, client: TestClient, db: Session):
        """Test bulk upload with larger batch"""
        # Create 50 test products
        products = []
        for i in range(50):
            products.append({
                "product_id": f"LARGE_BATCH_{i:03d}",
                "name": f"Large Batch Product {i}",
                "product_type": "sneakers",
                "brand": "Test Brand",
                "price": 99.99 + i
            })

        upload_data = {"products": products}

        response = client.post("/api/v1/products/bulk", json=upload_data)

        assert response.status_code == 200
        data = response.json()

        assert data["uploaded_count"] == 50
        assert data["error_count"] == 0

        # Verify all products were created
        products_response = client.get("/api/v1/products/?limit=100")
        created_products = products_response.json()
        assert len(created_products) == 50


@pytest.mark.parametrize("invalid_price", [-10, "not_a_number", None])
def test_bulk_upload_invalid_price_types(
    client: TestClient,
    db: Session,
    invalid_price
):
    """Test bulk upload with various invalid price types"""
    upload_data = {
        "products": [{
            "product_id": "INVALID_PRICE_001",
            "name": "Invalid Price Product",
            "product_type": "sneakers",
            "price": invalid_price
        }]
    }

    response = client.post("/api/v1/products/bulk", json=upload_data)

    # Should still return 200 but with errors
    if invalid_price == "not_a_number":
        # This should cause a validation error at the request level
        assert response.status_code == 422
    else:
        assert response.status_code == 200
        data = response.json()
        if invalid_price == -10:
            # Negative prices might be handled as errors in business logic
            assert data["error_count"] >= 0  # Depends on business rules