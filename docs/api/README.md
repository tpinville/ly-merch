# 🔌 API Documentation

The LY-Merch backend API is built with FastAPI and provides comprehensive REST endpoints for managing fashion trends and product data.

## 📍 Base URL

- **Development**: `http://localhost:8001`
- **Docker**: `http://localhost:8001`

## 🔐 Authentication

Currently, the API does not require authentication. This will be added in future versions.

## 📊 Core Endpoints

### Health & Status

```http
GET /health
```
Returns API health status.

```http
GET /api/v1/stats
```
Returns database statistics and counts.

### Products

#### List Products
```http
GET /api/v1/products
```

**Query Parameters:**
- `skip` (int): Number of records to skip (default: 0)
- `limit` (int): Maximum records to return (default: 100)
- `category_name` (string): Filter by category name
- `brand` (string): Filter by brand
- `min_price` (float): Minimum price filter
- `max_price` (float): Maximum price filter
- `availability_status` (string): Filter by status (`in_stock`, `out_of_stock`, `discontinued`, `pre_order`)

**Response:**
```json
[
  {
    "id": 1,
    "product_id": "NIKE_001",
    "name": "Air Max 90",
    "product_type": "sneakers",
    "brand": "Nike",
    "price": 120.00,
    "currency": "USD",
    "availability_status": "in_stock",
    "created_at": "2024-01-01T00:00:00",
    "trend": {
      "id": 1,
      "name": "Urban Athletic"
    }
  }
]
```

#### Get Single Product
```http
GET /api/v1/products/{product_id}
```

#### Bulk Upload Products
```http
POST /api/v1/products/bulk
```

**Request Body:**
```json
{
  "products": [
    {
      "product_id": "NIKE_001",
      "name": "Air Max 90",
      "product_type": "sneakers",
      "brand": "Nike",
      "price": 120.00,
      "currency": "USD",
      "color": "White/Black",
      "size": "10",
      "gender": "male",
      "availability_status": "in_stock",
      "trend_id": 1
    }
  ]
}
```

**Response:**
```json
{
  "uploaded_count": 15,
  "skipped_count": 2,
  "error_count": 1,
  "errors": [
    "Row 18: Invalid product_type 'invalid_type'"
  ]
}
```

### Categories

#### List Categories
```http
GET /api/v1/categories
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "sneakers",
    "created_at": "2024-01-01T00:00:00"
  }
]
```

### Verticals

#### List Verticals
```http
GET /api/v1/verticals
```

**Query Parameters:**
- `category_id` (int): Filter by category ID

### Trends

#### List Trends
```http
GET /api/v1/trends
```

**Query Parameters:**
- `vertical_id` (int): Filter by vertical ID
- `limit` (int): Maximum records to return

#### Get Trend with Images
```http
GET /api/v1/trends/{trend_id}
```

## 📋 Data Models

### Product
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| product_id | string | Yes | Unique product identifier |
| name | string | Yes | Product name |
| product_type | string | Yes | Product category type |
| brand | string | No | Brand name |
| price | float | No | Product price |
| currency | string | No | Currency code (default: USD) |
| color | string | No | Product color |
| size | string | No | Product size |
| material | string | No | Product material |
| gender | string | No | Target gender (male, female, unisex) |
| season | string | No | Target season |
| availability_status | string | No | Stock status |
| image_url | string | No | Product image URL |
| product_url | string | No | Product page URL |
| trend_id | int | No | Associated trend ID |

### Trend
| Field | Type | Description |
|-------|------|-------------|
| id | int | Database ID |
| trend_id | string | Unique trend identifier |
| name | string | Trend name |
| description | string | Trend description |
| vertical_id | int | Parent vertical ID |

### Category
| Field | Type | Description |
|-------|------|-------------|
| id | int | Database ID |
| name | string | Category name |

## 🚀 Usage Examples

### Python Requests
```python
import requests

# Get all products
response = requests.get('http://localhost:8001/api/v1/products')
products = response.json()

# Filter products
response = requests.get('http://localhost:8001/api/v1/products', params={
    'category_name': 'sneakers',
    'brand': 'Nike',
    'min_price': 50,
    'max_price': 200
})

# Bulk upload
payload = {
    'products': [
        {
            'product_id': 'NIKE_001',
            'name': 'Air Max 90',
            'product_type': 'sneakers',
            'brand': 'Nike',
            'price': 120.00
        }
    ]
}
response = requests.post('http://localhost:8001/api/v1/products/bulk', json=payload)
```

### cURL Examples
```bash
# Get products with filters
curl "http://localhost:8001/api/v1/products?category_name=sneakers&limit=10"

# Bulk upload
curl -X POST "http://localhost:8001/api/v1/products/bulk" \
  -H "Content-Type: application/json" \
  -d @data/sample_products.json

# Get API health
curl "http://localhost:8001/health"
```

## ⚠️ Error Handling

The API returns standard HTTP status codes:

- `200` - Success
- `400` - Bad Request (validation error)
- `404` - Resource not found
- `422` - Unprocessable Entity (validation error)
- `500` - Internal Server Error

Error responses include detailed information:
```json
{
  "detail": "Validation error message",
  "errors": [
    {
      "loc": ["products", 0, "price"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt"
    }
  ]
}
```

## 🔄 Rate Limiting

Currently no rate limiting is implemented. This will be added in future versions.

## 📝 OpenAPI Documentation

Interactive API documentation is available at:
- **Swagger UI**: `http://localhost:8001/docs`
- **ReDoc**: `http://localhost:8001/redoc`