# 🧪 LY-Merch API Test Suite

Comprehensive functional tests for the LY-Merch Fashion Trends API.

## 📋 Overview

This test suite provides complete coverage of all API endpoints with:
- **Unit tests** for individual functions and endpoints
- **Integration tests** for full workflow scenarios
- **Functional tests** for all CRUD operations
- **Validation tests** for data integrity and error handling
- **Performance tests** for bulk operations

## 🗂️ Test Structure

```
tests/
├── conftest.py                     # Test configuration and fixtures
├── test_health_and_stats.py       # Health check and statistics endpoints
├── test_categories.py             # Categories CRUD operations
├── test_verticals.py              # Verticals endpoints
├── test_trends.py                 # Trends endpoints and full-text search
├── test_images.py                 # Images endpoints and statistics
├── test_products.py               # Products CRUD and bulk upload
└── test_validation_and_errors.py  # Data validation and error handling
```

## 🚀 Running Tests

### Quick Start

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_products.py

# Run with verbose output
pytest -v
```

### Using Test Runner Script

```bash
# Run all tests with coverage
../scripts/run-api-tests.sh

# Run tests in parallel
../scripts/run-api-tests.sh --parallel

# Run specific pattern
../scripts/run-api-tests.sh --pattern "test_products.py"

# Skip integration tests
../scripts/run-api-tests.sh --no-integration
```

### Integration Tests

```bash
# Start API server first
docker-compose up -d api

# Run integration tests
python3 ../scripts/test-api-integration.py

# Or specify different API URL
python3 ../scripts/test-api-integration.py http://localhost:8001
```

## 🎯 Test Categories

### Health & Statistics Tests
- API health check endpoint
- Database connection status
- Statistics aggregation
- Root endpoint information

### Categories Tests
- List all categories with pagination
- Get single category by ID
- Search categories by name
- Vertical count validation
- Error handling for invalid IDs

### Verticals Tests
- List verticals with filtering
- Filter by category, geo zone, and name
- Get single vertical with/without trends
- Geo zones endpoint
- Pagination and validation

### Trends Tests
- List trends with complex filtering
- Filter by vertical, category, and images
- Get single trend with/without images
- Full-text search functionality
- Image count aggregation

### Images Tests
- List images with filtering
- Filter by trend and image type
- Get single image by ID
- Image statistics
- Pagination validation

### Products Tests (Most Comprehensive)
- **CRUD Operations**: Create, read, update, delete products
- **List and Filter**: Search by name, brand, type, price range, availability
- **Bulk Upload**: CSV-style bulk product creation
- **Duplicate Handling**: Skip existing products
- **Auto-ID Generation**: Generate IDs when not provided
- **Data Validation**: Price validation, enum validation, required fields
- **Error Recovery**: Partial success handling
- **Statistics**: Product distribution and analytics

### Validation & Error Tests
- **Parameter Validation**: Invalid limits, offsets, filters
- **Path Parameter Validation**: Invalid IDs and types
- **Request Body Validation**: Missing fields, invalid types
- **Business Logic Validation**: Negative prices, empty names
- **Error Response Format**: Consistent error structures
- **Bulk Upload Edge Cases**: Large batches, duplicates, invalid data

## 🔧 Test Configuration

### pytest.ini Configuration
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
addopts =
    -v
    --cov=app
    --cov-report=term-missing
    --cov-fail-under=80
```

### Test Fixtures

The test suite uses comprehensive fixtures for:
- **Database setup**: In-memory SQLite for fast tests
- **Sample data**: Categories, verticals, trends, images, products
- **Bulk test data**: Valid and invalid product batches
- **API client**: Pre-configured TestClient

## 📊 Coverage Goals

- **Overall Coverage**: 80%+ line coverage
- **Endpoint Coverage**: 100% of API endpoints tested
- **Error Path Coverage**: All error conditions tested
- **Business Logic Coverage**: All validation rules tested

## 🎨 Test Data

### Sample Data Structure
```python
# Category
category = Category(name="sneakers", description="Athletic sneakers")

# Vertical
vertical = Vertical(
    vertical_id="sneakers:nike_us",
    category=category,
    name="Nike US",
    geo_zone="US"
)

# Trend
trend = Trend(
    trend_id="athletic_001",
    vertical=vertical,
    name="Urban Athletic",
    description="Modern athletic footwear trends"
)

# Product
product = Product(
    product_id="NIKE_AIR_001",
    trend=trend,
    name="Nike Air Max 90",
    product_type="sneakers",
    brand="Nike",
    price=129.99,
    availability_status="in_stock"
)
```

## 🚨 Error Testing

The test suite comprehensively tests error conditions:

### Validation Errors (422)
- Invalid parameter types
- Out-of-range values
- Missing required fields
- Invalid enum values

### Not Found Errors (404)
- Non-existent resource IDs
- Invalid resource paths

### Business Logic Errors
- Duplicate product IDs
- Invalid foreign key references
- Constraint violations

## 🔄 Continuous Integration

Tests are configured for CI/CD pipelines:

### GitHub Actions Integration
```yaml
- name: Run API Tests
  run: |
    cd api
    pip install -r requirements-test.txt
    pytest --cov=app --cov-report=xml
```

### Docker Integration
```bash
# Run tests in Docker environment
docker-compose exec api pytest tests/
```

## 📈 Performance Testing

### Bulk Operations
- Upload 1000+ products in single batch
- Concurrent upload handling
- Memory usage validation
- Response time measurement

### Pagination Performance
- Large dataset pagination
- Offset performance with large offsets
- Filter performance with complex queries

## 🛠️ Development Workflow

### Adding New Tests

1. **Create test file** following naming convention `test_*.py`
2. **Import required fixtures** from `conftest.py`
3. **Use descriptive test names** describing the scenario
4. **Follow AAA pattern**: Arrange, Act, Assert
5. **Add appropriate markers** for test categorization

### Test Structure Example
```python
class TestProductEndpoint:
    """Test product-related endpoints"""

    def test_create_product_success(self, client, sample_trend):
        """Test successful product creation"""
        # Arrange
        product_data = {
            "product_id": "TEST_001",
            "name": "Test Product",
            "product_type": "sneakers",
            "trend_id": sample_trend.id
        }

        # Act
        response = client.post("/api/v1/products/", json=product_data)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["product_id"] == "TEST_001"
```

## 🎯 Best Practices

1. **Isolation**: Each test is independent and can run alone
2. **Cleanup**: Tests clean up their data automatically
3. **Realistic Data**: Tests use realistic sample data
4. **Error Coverage**: Both success and failure paths tested
5. **Performance Aware**: Tests avoid unnecessary database operations
6. **Maintainable**: Tests are readable and well-documented

## 📚 Resources

- [pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites)
- [Test-Driven Development](https://testdriven.io/)