"""
Test configuration and fixtures for API functional tests
"""

import os
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_db, Base
from app.models import Category, Vertical, Trend, TrendImage, Product

# Test database URL (in-memory SQLite for testing)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# Create test engine with specific configuration for SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "check_same_thread": False,
        "timeout": 20
    },
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override the dependency
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def test_engine():
    """Test database engine fixture"""
    return engine


@pytest.fixture(scope="session")
def test_db_session():
    """Test database session fixture"""
    # Create all tables
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    yield session

    session.close()
    # Drop all tables after tests
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """Fresh database session for each test"""
    # Create all tables
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Clean up tables after each test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def client():
    """FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def sample_category(db: Session):
    """Create a sample category for testing"""
    category = Category(
        name="test_sneakers",
        description="Test sneakers category"
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@pytest.fixture
def sample_vertical(db: Session, sample_category):
    """Create a sample vertical for testing"""
    vertical = Vertical(
        vertical_id="test_sneakers:nike_us",
        category_id=sample_category.id,
        name="Nike US Test Vertical",
        geo_zone="US"
    )
    db.add(vertical)
    db.commit()
    db.refresh(vertical)
    return vertical


@pytest.fixture
def sample_trend(db: Session, sample_vertical):
    """Create a sample trend for testing"""
    trend = Trend(
        trend_id="test_trend_001",
        vertical_id=sample_vertical.id,
        name="Test Athletic Trend",
        description="A test trend for athletic footwear",
        image_hash="test_hash_123"
    )
    db.add(trend)
    db.commit()
    db.refresh(trend)
    return trend


@pytest.fixture
def sample_trend_image(db: Session, sample_trend):
    """Create a sample trend image for testing"""
    image = TrendImage(
        trend_id=sample_trend.id,
        image_type="positive",
        md5_hash="test_md5_hash_123",
        description="Test positive image"
    )
    db.add(image)
    db.commit()
    db.refresh(image)
    return image


@pytest.fixture
def sample_product(db: Session, sample_trend):
    """Create a sample product for testing"""
    product = Product(
        product_id="TEST_NIKE_001",
        trend_id=sample_trend.id,
        name="Test Nike Air Max",
        product_type="sneakers",
        description="Test product description",
        brand="Nike",
        price=129.99,
        currency="USD",
        color="White/Black",
        size="10",
        material="Leather/Mesh",
        gender="male",
        season="all",
        availability_status="in_stock",
        image_url="https://example.com/test-image.jpg",
        product_url="https://example.com/test-product"
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@pytest.fixture
def multiple_categories(db: Session):
    """Create multiple categories for testing"""
    categories = [
        Category(name="sneakers", description="Athletic sneakers"),
        Category(name="boots", description="Fashion boots"),
        Category(name="sandals", description="Summer sandals")
    ]

    for category in categories:
        db.add(category)

    db.commit()

    for category in categories:
        db.refresh(category)

    return categories


@pytest.fixture
def multiple_products(db: Session, sample_trend):
    """Create multiple products for testing"""
    products = [
        Product(
            product_id="TEST_001",
            trend_id=sample_trend.id,
            name="Test Product 1",
            product_type="sneakers",
            brand="Nike",
            price=99.99,
            currency="USD",
            availability_status="in_stock",
            gender="male"
        ),
        Product(
            product_id="TEST_002",
            trend_id=sample_trend.id,
            name="Test Product 2",
            product_type="sneakers",
            brand="Adidas",
            price=89.99,
            currency="USD",
            availability_status="out_of_stock",
            gender="female"
        ),
        Product(
            product_id="TEST_003",
            trend_id=sample_trend.id,
            name="Test Product 3",
            product_type="boots",
            brand="Dr. Martens",
            price=159.99,
            currency="USD",
            availability_status="in_stock",
            gender="unisex"
        )
    ]

    for product in products:
        db.add(product)

    db.commit()

    for product in products:
        db.refresh(product)

    return products


@pytest.fixture
def bulk_upload_data():
    """Sample data for bulk upload testing"""
    return {
        "products": [
            {
                "product_id": "BULK_001",
                "name": "Bulk Test Product 1",
                "product_type": "sneakers",
                "brand": "Test Brand",
                "price": 79.99,
                "currency": "USD",
                "color": "Red",
                "size": "9",
                "gender": "male",
                "availability_status": "in_stock"
            },
            {
                "product_id": "BULK_002",
                "name": "Bulk Test Product 2",
                "product_type": "boots",
                "brand": "Test Brand",
                "price": 119.99,
                "currency": "USD",
                "color": "Brown",
                "size": "10",
                "gender": "female",
                "availability_status": "pre_order"
            }
        ]
    }


@pytest.fixture
def invalid_bulk_upload_data():
    """Invalid sample data for bulk upload error testing"""
    return {
        "products": [
            {
                # Missing required fields
                "name": "Invalid Product",
                "price": "not_a_number"  # Invalid price type
            },
            {
                "product_id": "INVALID_001",
                "name": "",  # Empty name
                "product_type": "invalid_type",
                "price": -50.0  # Negative price
            }
        ]
    }