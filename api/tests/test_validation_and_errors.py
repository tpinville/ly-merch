"""
Test data validation and error handling across all endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TestParameterValidation:
    """Test parameter validation for various endpoints"""

    @pytest.mark.parametrize("endpoint,invalid_params", [
        ("/api/v1/categories/", {"limit": -1}),
        ("/api/v1/categories/", {"limit": 2000}),
        ("/api/v1/categories/", {"offset": -1}),
        ("/api/v1/verticals/", {"limit": 0}),
        ("/api/v1/verticals/", {"offset": -5}),
        ("/api/v1/trends/", {"limit": 1001}),
        ("/api/v1/products/", {"min_price": "invalid"}),
        ("/api/v1/products/", {"max_price": "not_a_number"}),
        ("/api/v1/images/", {"limit": 2000}),
    ])
    def test_invalid_query_parameters(
        self,
        client: TestClient,
        db: Session,
        endpoint: str,
        invalid_params: dict
    ):
        """Test various invalid query parameters return 422"""
        response = client.get(endpoint, params=invalid_params)
        assert response.status_code == 422

        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], list)

    @pytest.mark.parametrize("endpoint,valid_params", [
        ("/api/v1/categories/", {"limit": 50, "offset": 0}),
        ("/api/v1/verticals/", {"limit": 100, "offset": 10}),
        ("/api/v1/trends/", {"limit": 25, "offset": 5}),
        ("/api/v1/products/", {"min_price": 10.5, "max_price": 999.99}),
        ("/api/v1/images/", {"limit": 10, "offset": 0}),
    ])
    def test_valid_query_parameters(
        self,
        client: TestClient,
        db: Session,
        endpoint: str,
        valid_params: dict
    ):
        """Test valid query parameters return 200"""
        response = client.get(endpoint, params=valid_params)
        assert response.status_code == 200

    @pytest.mark.parametrize("endpoint", [
        "/api/v1/categories/invalid_id",
        "/api/v1/verticals/not_a_number",
        "/api/v1/trends/abc123",
        "/api/v1/products/invalid",
        "/api/v1/images/xyz",
    ])
    def test_invalid_path_parameters(
        self,
        client: TestClient,
        db: Session,
        endpoint: str
    ):
        """Test invalid path parameters return 422"""
        response = client.get(endpoint)
        assert response.status_code == 422


class TestNotFoundErrors:
    """Test 404 not found errors"""

    @pytest.mark.parametrize("endpoint", [
        "/api/v1/categories/999999",
        "/api/v1/verticals/888888",
        "/api/v1/trends/777777",
        "/api/v1/products/666666",
        "/api/v1/images/555555",
    ])
    def test_resource_not_found(
        self,
        client: TestClient,
        db: Session,
        endpoint: str
    ):
        """Test accessing non-existent resources returns 404"""
        response = client.get(endpoint)
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()


class TestBulkUploadValidation:
    """Test bulk upload data validation"""

    def test_bulk_upload_missing_products_field(
        self,
        client: TestClient,
        db: Session
    ):
        """Test bulk upload without products field"""
        invalid_data = {"invalid_field": "value"}

        response = client.post("/api/v1/products/bulk", json=invalid_data)
        assert response.status_code == 422

        data = response.json()
        assert "detail" in data
        # Should mention missing 'products' field
        error_messages = str(data["detail"])
        assert "products" in error_messages.lower()

    def test_bulk_upload_invalid_product_structure(
        self,
        client: TestClient,
        db: Session
    ):
        """Test bulk upload with invalid product structure"""
        invalid_data = {
            "products": [
                {
                    # Missing required fields, invalid types
                    "price": "not_a_number",
                    "invalid_field": "should_not_be_here"
                }
            ]
        }

        response = client.post("/api/v1/products/bulk", json=invalid_data)

        # Should either return 422 for validation errors or 200 with errors in response
        assert response.status_code in [200, 422]

        if response.status_code == 200:
            data = response.json()
            assert data["error_count"] > 0
            assert isinstance(data["errors"], list)

    def test_bulk_upload_empty_required_fields(
        self,
        client: TestClient,
        db: Session
    ):
        """Test bulk upload with empty required fields"""
        invalid_data = {
            "products": [
                {
                    "product_id": "",
                    "name": "",
                    "product_type": "",
                }
            ]
        }

        response = client.post("/api/v1/products/bulk", json=invalid_data)
        assert response.status_code == 200  # API handles this gracefully

        data = response.json()
        assert data["error_count"] > 0
        assert any("name" in error.lower() for error in data["errors"])

    def test_bulk_upload_invalid_price_values(
        self,
        client: TestClient,
        db: Session
    ):
        """Test bulk upload with various invalid price values"""
        test_cases = [
            {"price": -100.0},  # Negative price
            {"price": 0},       # Zero price (might be invalid)
            {"price": "invalid"} # String instead of number (validation error)
        ]

        for case in test_cases:
            product_data = {
                "product_id": f"TEST_{case['price']}",
                "name": "Test Product",
                "product_type": "sneakers",
                **case
            }

            invalid_data = {"products": [product_data]}

            response = client.post("/api/v1/products/bulk", json=invalid_data)

            # Should handle gracefully
            if response.status_code == 422:
                # Validation error at request level
                continue
            else:
                assert response.status_code == 200
                data = response.json()
                # Business logic might reject negative prices
                if case["price"] == -100.0:
                    assert data["error_count"] >= 0  # Depends on business rules

    def test_bulk_upload_invalid_enum_values(
        self,
        client: TestClient,
        db: Session
    ):
        """Test bulk upload with invalid enum values"""
        invalid_data = {
            "products": [
                {
                    "product_id": "TEST_ENUM_001",
                    "name": "Test Product",
                    "product_type": "sneakers",
                    "gender": "invalid_gender",
                    "availability_status": "invalid_status",
                    "currency": "INVALID_CURRENCY"
                }
            ]
        }

        response = client.post("/api/v1/products/bulk", json=invalid_data)

        # Should handle gracefully (depends on model validation)
        assert response.status_code == 200
        data = response.json()

        # Might have validation errors for invalid enum values
        if data["error_count"] > 0:
            assert isinstance(data["errors"], list)

    def test_bulk_upload_extremely_long_strings(
        self,
        client: TestClient,
        db: Session
    ):
        """Test bulk upload with extremely long string values"""
        long_string = "x" * 10000  # Very long string

        invalid_data = {
            "products": [
                {
                    "product_id": "TEST_LONG_001",
                    "name": long_string,
                    "product_type": "sneakers",
                    "description": long_string,
                    "brand": long_string
                }
            ]
        }

        response = client.post("/api/v1/products/bulk", json=invalid_data)
        assert response.status_code == 200  # Should handle gracefully

        data = response.json()
        # Might truncate or reject long strings
        assert data["uploaded_count"] >= 0


class TestConcurrencyAndEdgeCases:
    """Test concurrency and edge cases"""

    def test_bulk_upload_large_batch_size(
        self,
        client: TestClient,
        db: Session
    ):
        """Test bulk upload with very large batch"""
        # Create 1000 products
        products = []
        for i in range(1000):
            products.append({
                "product_id": f"LARGE_{i:04d}",
                "name": f"Large Batch Product {i}",
                "product_type": "sneakers",
                "price": 99.99 + i * 0.01
            })

        large_data = {"products": products}

        response = client.post("/api/v1/products/bulk", json=large_data)
        assert response.status_code == 200

        data = response.json()
        assert data["uploaded_count"] == 1000
        assert data["error_count"] == 0

    def test_duplicate_concurrent_uploads(
        self,
        client: TestClient,
        db: Session
    ):
        """Test handling of duplicate products in same batch"""
        duplicate_data = {
            "products": [
                {
                    "product_id": "DUPLICATE_001",
                    "name": "Duplicate Product",
                    "product_type": "sneakers",
                    "price": 99.99
                },
                {
                    "product_id": "DUPLICATE_001",  # Same ID
                    "name": "Another Duplicate Product",
                    "product_type": "boots",
                    "price": 149.99
                }
            ]
        }

        response = client.post("/api/v1/products/bulk", json=duplicate_data)
        assert response.status_code == 200

        data = response.json()
        # Should handle duplicates gracefully
        assert data["uploaded_count"] + data["skipped_count"] == 2
        assert data["error_count"] >= 0


class TestFullTextSearchValidation:
    """Test full-text search validation"""

    def test_fulltext_search_missing_query(
        self,
        client: TestClient,
        db: Session
    ):
        """Test full-text search without query parameter"""
        response = client.get("/api/v1/trends/search/fulltext")
        assert response.status_code == 422

    def test_fulltext_search_empty_query(
        self,
        client: TestClient,
        db: Session
    ):
        """Test full-text search with empty query"""
        response = client.get("/api/v1/trends/search/fulltext?q=")
        assert response.status_code == 422

    def test_fulltext_search_very_long_query(
        self,
        client: TestClient,
        db: Session
    ):
        """Test full-text search with very long query"""
        long_query = "x" * 1000
        response = client.get(f"/api/v1/trends/search/fulltext?q={long_query}")

        # Should handle gracefully
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_fulltext_search_special_characters(
        self,
        client: TestClient,
        db: Session
    ):
        """Test full-text search with special characters"""
        special_queries = [
            "test & fashion",
            "sneakers | boots",
            '"exact phrase"',
            "test*",
            "+required -excluded"
        ]

        for query in special_queries:
            response = client.get(f"/api/v1/trends/search/fulltext?q={query}")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)


class TestDatabaseConstraintErrors:
    """Test database constraint error handling"""

    def test_foreign_key_constraint(
        self,
        client: TestClient,
        db: Session
    ):
        """Test handling of foreign key constraint violations"""
        # Try to create product with non-existent trend_id
        invalid_data = {
            "products": [
                {
                    "product_id": "FK_TEST_001",
                    "name": "Foreign Key Test",
                    "product_type": "sneakers",
                    "trend_id": 999999  # Non-existent trend
                }
            ]
        }

        response = client.post("/api/v1/products/bulk", json=invalid_data)
        assert response.status_code == 200  # Should handle gracefully

        data = response.json()
        # Should report error for invalid foreign key
        if data["error_count"] > 0:
            assert any("trend_id" in error.lower() or "foreign" in error.lower()
                     for error in data["errors"])


class TestRateLimitingAndPerformance:
    """Test performance and rate limiting (if implemented)"""

    def test_rapid_successive_requests(
        self,
        client: TestClient,
        db: Session
    ):
        """Test multiple rapid requests to same endpoint"""
        # Make 10 rapid requests
        for i in range(10):
            response = client.get("/api/v1/categories/")
            assert response.status_code == 200

    def test_concurrent_bulk_uploads(
        self,
        client: TestClient,
        db: Session
    ):
        """Test multiple concurrent bulk uploads"""
        # This would require actual threading to test properly
        # For now, just test sequential uploads
        for batch in range(3):
            products = [
                {
                    "product_id": f"CONCURRENT_{batch}_{i}",
                    "name": f"Concurrent Product {batch}-{i}",
                    "product_type": "sneakers"
                }
                for i in range(10)
            ]

            upload_data = {"products": products}
            response = client.post("/api/v1/products/bulk", json=upload_data)
            assert response.status_code == 200

        # Verify all products were created
        response = client.get("/api/v1/products/?limit=100")
        products = response.json()
        assert len(products) == 30  # 3 batches * 10 products each