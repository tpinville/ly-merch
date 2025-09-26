"""
API routers for fashion trends data
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, or_, text, case

from .database import get_db
from .models import (
    Category, Vertical, Trend, TrendImage, Product,
    CategoryResponse, VerticalResponse, VerticalSummaryResponse,
    TrendResponse, TrendSummaryResponse,
    TrendImageResponse, ProductResponse, ProductSummaryResponse,
    TrendSearchParams, VerticalSearchParams, ImageSearchParams, ProductSearchParams,
    ProductCreateRequest, ProductBulkUploadRequest, ProductBulkUploadResponse
)

# Create routers
categories_router = APIRouter(prefix="/categories", tags=["categories"])
verticals_router = APIRouter(prefix="/verticals", tags=["verticals"])
trends_router = APIRouter(prefix="/trends", tags=["trends"])
images_router = APIRouter(prefix="/images", tags=["images"])
products_router = APIRouter(prefix="/products", tags=["products"])


# CATEGORIES ENDPOINTS

@categories_router.get("/", response_model=List[CategoryResponse])
def get_categories(
    query: Optional[str] = Query(None, description="Search by name"),
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get list of all categories with vertical counts"""

    # Build base query with vertical count
    query_stmt = db.query(
        Category,
        func.count(Vertical.id).label('vertical_count')
    ).outerjoin(Vertical).group_by(Category.id)

    # Apply filters
    if query:
        query_stmt = query_stmt.filter(Category.name.contains(query))

    # Apply pagination and ordering
    query_stmt = query_stmt.order_by(Category.name).offset(offset).limit(limit)

    results = query_stmt.all()

    return [
        CategoryResponse(
            id=category.id,
            name=category.name,
            description=category.description,
            created_at=category.created_at,
            updated_at=category.updated_at,
            vertical_count=vertical_count
        )
        for category, vertical_count in results
    ]


@categories_router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """Get a specific category by ID"""

    category = db.query(Category).filter(Category.id == category_id).first()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Get vertical count
    vertical_count = db.query(func.count(Vertical.id)).filter(Vertical.category_id == category.id).scalar() or 0

    return CategoryResponse(
        id=category.id,
        name=category.name,
        description=category.description,
        created_at=category.created_at,
        updated_at=category.updated_at,
        vertical_count=vertical_count
    )


# VERTICALS ENDPOINTS

@verticals_router.get("/", response_model=List[VerticalSummaryResponse])
def get_verticals(
    geo_zone: Optional[str] = Query(None, description="Filter by geo zone"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    category_name: Optional[str] = Query(None, description="Filter by category name"),
    query: Optional[str] = Query(None, description="Search by name"),
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get list of all verticals with trend counts and category information"""

    # Build base query with trend count and category information
    query_stmt = db.query(
        Vertical,
        Category.name.label('category_name'),
        func.count(Trend.id).label('trend_count')
    ).join(Category).outerjoin(Trend).group_by(Vertical.id)

    # Apply filters
    if geo_zone:
        query_stmt = query_stmt.filter(Vertical.geo_zone == geo_zone)

    if category_id:
        query_stmt = query_stmt.filter(Vertical.category_id == category_id)

    if category_name:
        query_stmt = query_stmt.filter(Category.name.contains(category_name))

    if query:
        query_stmt = query_stmt.filter(Vertical.name.contains(query))

    # Apply pagination and ordering
    query_stmt = query_stmt.order_by(Vertical.name).offset(offset).limit(limit)

    results = query_stmt.all()

    return [
        VerticalSummaryResponse(
            id=vertical.id,
            vertical_id=vertical.vertical_id,
            category_id=vertical.category_id,
            category_name=category_name,
            name=vertical.name,
            geo_zone=vertical.geo_zone,
            trend_count=trend_count
        )
        for vertical, category_name, trend_count in results
    ]


@verticals_router.get("/{vertical_id}", response_model=VerticalResponse)
def get_vertical(vertical_id: int, include_trends: bool = Query(False), db: Session = Depends(get_db)):
    """Get a specific vertical by ID with category information"""

    query_stmt = db.query(Vertical).options(joinedload(Vertical.category))
    if include_trends:
        query_stmt = query_stmt.options(joinedload(Vertical.trends))

    vertical = query_stmt.filter(Vertical.id == vertical_id).first()

    if not vertical:
        raise HTTPException(status_code=404, detail="Vertical not found")

    # Get trend count and details if requested
    if include_trends and vertical.trends:
        trends_data = []
        for trend in vertical.trends:
            # Get image counts for each trend
            image_counts = db.query(
                func.count(TrendImage.id).label('total'),
                func.sum(
                    case((TrendImage.image_type == 'positive', 1), else_=0)
                ).label('positive'),
                func.sum(
                    case((TrendImage.image_type == 'negative', 1), else_=0)
                ).label('negative')
            ).filter(TrendImage.trend_id == trend.id).first()

            trends_data.append(TrendSummaryResponse(
                id=trend.id,
                trend_id=trend.trend_id,
                name=trend.name,
                description=trend.description,
                image_hash=trend.image_hash,
                image_count=image_counts.total or 0,
                positive_image_count=image_counts.positive or 0,
                negative_image_count=image_counts.negative or 0
            ))

        return VerticalResponse(
            id=vertical.id,
            vertical_id=vertical.vertical_id,
            category_id=vertical.category_id,
            category_name=vertical.category.name if vertical.category else None,
            category_description=vertical.category.description if vertical.category else None,
            name=vertical.name,
            geo_zone=vertical.geo_zone,
            created_at=vertical.created_at,
            updated_at=vertical.updated_at,
            trends=trends_data,
            trend_count=len(trends_data)
        )
    else:
        trend_count = db.query(func.count(Trend.id)).filter(Trend.vertical_id == vertical.id).scalar() or 0

        return VerticalResponse(
            id=vertical.id,
            vertical_id=vertical.vertical_id,
            category_id=vertical.category_id,
            category_name=vertical.category.name if vertical.category else None,
            category_description=vertical.category.description if vertical.category else None,
            name=vertical.name,
            geo_zone=vertical.geo_zone,
            created_at=vertical.created_at,
            updated_at=vertical.updated_at,
            trend_count=trend_count
        )


@verticals_router.get("/search/geo-zones")
def get_geo_zones(db: Session = Depends(get_db)):
    """Get list of available geo zones"""
    zones = db.query(Vertical.geo_zone).distinct().all()
    return [zone[0] for zone in zones]


# TRENDS ENDPOINTS

@trends_router.get("/", response_model=List[TrendSummaryResponse])
def get_trends(
    vertical_id: Optional[int] = Query(None, description="Filter by vertical ID"),
    vertical_name: Optional[str] = Query(None, description="Filter by vertical name"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    category_name: Optional[str] = Query(None, description="Filter by category name"),
    geo_zone: Optional[str] = Query(None, description="Filter by geo zone"),
    query: Optional[str] = Query(None, description="Search in trend name or description"),
    has_images: Optional[bool] = Query(None, description="Filter trends that have/don't have images"),
    image_type: Optional[str] = Query(None, description="Filter by image type (positive/negative)"),
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Search and filter trends with category support"""

    # Build base query with image counts, including category joins
    query_stmt = db.query(
        Trend,
        func.count(TrendImage.id).label('image_count'),
        func.sum(
            case((TrendImage.image_type == 'positive', 1), else_=0)
        ).label('positive_count'),
        func.sum(
            case((TrendImage.image_type == 'negative', 1), else_=0)
        ).label('negative_count')
    ).outerjoin(TrendImage).outerjoin(Vertical).outerjoin(Category).group_by(Trend.id)

    # Apply filters
    if vertical_id:
        query_stmt = query_stmt.filter(Trend.vertical_id == vertical_id)

    if vertical_name:
        query_stmt = query_stmt.filter(Vertical.name.contains(vertical_name))

    if category_id:
        query_stmt = query_stmt.filter(Vertical.category_id == category_id)

    if category_name:
        query_stmt = query_stmt.filter(Category.name.contains(category_name))

    if geo_zone:
        query_stmt = query_stmt.filter(Vertical.geo_zone == geo_zone)

    if query:
        query_stmt = query_stmt.filter(
            or_(
                Trend.name.contains(query),
                Trend.description.contains(query)
            )
        )

    if has_images is not None:
        if has_images:
            query_stmt = query_stmt.having(func.count(TrendImage.id) > 0)
        else:
            query_stmt = query_stmt.having(func.count(TrendImage.id) == 0)

    if image_type:
        query_stmt = query_stmt.filter(TrendImage.image_type == image_type)

    # Apply pagination and ordering
    query_stmt = query_stmt.order_by(Trend.name).offset(offset).limit(limit)

    results = query_stmt.all()

    return [
        TrendSummaryResponse(
            id=trend.id,
            trend_id=trend.trend_id,
            name=trend.name,
            description=trend.description,
            image_hash=trend.image_hash,
            image_count=image_count or 0,
            positive_image_count=positive_count or 0,
            negative_image_count=negative_count or 0
        )
        for trend, image_count, positive_count, negative_count in results
    ]


@trends_router.get("/{trend_id}", response_model=TrendResponse)
def get_trend(
    trend_id: int,
    include_images: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Get a specific trend by ID"""

    query_stmt = db.query(Trend)
    if include_images:
        query_stmt = query_stmt.options(joinedload(Trend.images))

    trend = query_stmt.filter(Trend.id == trend_id).first()

    if not trend:
        raise HTTPException(status_code=404, detail="Trend not found")

    if include_images:
        return TrendResponse(
            id=trend.id,
            trend_id=trend.trend_id,
            name=trend.name,
            description=trend.description,
            image_hash=trend.image_hash,
            created_at=trend.created_at,
            updated_at=trend.updated_at,
            images=[
                TrendImageResponse(
                    id=img.id,
                    image_type=img.image_type,
                    md5_hash=img.md5_hash,
                    description=img.description,
                    created_at=img.created_at,
                    updated_at=img.updated_at
                )
                for img in trend.images
            ]
        )
    else:
        return TrendResponse(
            id=trend.id,
            trend_id=trend.trend_id,
            name=trend.name,
            description=trend.description,
            image_hash=trend.image_hash,
            created_at=trend.created_at,
            updated_at=trend.updated_at
        )


@trends_router.get("/search/fulltext")
def fulltext_search(
    q: str = Query(..., description="Full-text search query"),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Full-text search in trend descriptions using MySQL MATCH AGAINST"""

    try:
        query_stmt = db.query(Trend).filter(
            text("MATCH(description) AGAINST(:search_term IN BOOLEAN MODE)")
        ).params(search_term=q).limit(limit)

        trends = query_stmt.all()

        return [
            {
                "id": trend.id,
                "trend_id": trend.trend_id,
                "name": trend.name,
                "description": trend.description[:200] + "..." if trend.description and len(trend.description) > 200 else trend.description
            }
            for trend in trends
        ]
    except Exception as e:
        # Fallback to LIKE search if fulltext fails
        trends = db.query(Trend).filter(
            Trend.description.contains(q)
        ).limit(limit).all()

        return [
            {
                "id": trend.id,
                "trend_id": trend.trend_id,
                "name": trend.name,
                "description": trend.description[:200] + "..." if trend.description and len(trend.description) > 200 else trend.description
            }
            for trend in trends
        ]


# IMAGES ENDPOINTS

@images_router.get("/", response_model=List[TrendImageResponse])
def get_images(
    trend_id: Optional[int] = Query(None, description="Filter by trend ID"),
    image_type: Optional[str] = Query(None, description="Filter by type (positive/negative)"),
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get trend images with filters"""

    query_stmt = db.query(TrendImage)

    if trend_id:
        query_stmt = query_stmt.filter(TrendImage.trend_id == trend_id)

    if image_type:
        query_stmt = query_stmt.filter(TrendImage.image_type == image_type)

    query_stmt = query_stmt.order_by(TrendImage.id).offset(offset).limit(limit)

    images = query_stmt.all()

    return [
        TrendImageResponse(
            id=img.id,
            image_type=img.image_type,
            md5_hash=img.md5_hash,
            description=img.description,
            created_at=img.created_at,
            updated_at=img.updated_at
        )
        for img in images
    ]


@images_router.get("/{image_id}", response_model=TrendImageResponse)
def get_image(image_id: int, db: Session = Depends(get_db)):
    """Get a specific image by ID"""

    image = db.query(TrendImage).filter(TrendImage.id == image_id).first()

    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    return TrendImageResponse(
        id=image.id,
        image_type=image.image_type,
        md5_hash=image.md5_hash,
        description=image.description,
        created_at=image.created_at,
        updated_at=image.updated_at
    )


# PRODUCTS ENDPOINTS

@products_router.get("/", response_model=List[ProductSummaryResponse])
def get_products(
    query: Optional[str] = Query(None, description="Search in product name or description"),
    trend_id: Optional[int] = Query(None, description="Filter by trend ID"),
    product_type: Optional[str] = Query(None, description="Filter by product type (e.g., t-shirt, sneakers)"),
    brand: Optional[str] = Query(None, description="Filter by brand"),
    gender: Optional[str] = Query(None, description="Filter by gender"),
    availability_status: Optional[str] = Query(None, description="Filter by availability status"),
    min_price: Optional[float] = Query(None, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, description="Maximum price filter"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    category_name: Optional[str] = Query(None, description="Filter by category name"),
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Search and filter products"""

    # Build base query
    query_stmt = db.query(Product).outerjoin(Trend).outerjoin(Vertical).outerjoin(Category)

    # Apply filters
    if trend_id:
        query_stmt = query_stmt.filter(Product.trend_id == trend_id)

    if product_type:
        query_stmt = query_stmt.filter(Product.product_type.contains(product_type))

    if brand:
        query_stmt = query_stmt.filter(Product.brand.contains(brand))

    if gender:
        query_stmt = query_stmt.filter(Product.gender == gender)

    if availability_status:
        query_stmt = query_stmt.filter(Product.availability_status == availability_status)

    if min_price is not None:
        query_stmt = query_stmt.filter(Product.price >= min_price)

    if max_price is not None:
        query_stmt = query_stmt.filter(Product.price <= max_price)

    if category_id:
        query_stmt = query_stmt.filter(Vertical.category_id == category_id)

    if category_name:
        query_stmt = query_stmt.filter(Category.name.contains(category_name))

    if query:
        query_stmt = query_stmt.filter(
            or_(
                Product.name.contains(query),
                Product.description.contains(query)
            )
        )

    # Apply pagination and ordering
    query_stmt = query_stmt.order_by(Product.name).offset(offset).limit(limit)

    products = query_stmt.all()

    return [
        ProductSummaryResponse(
            id=product.id,
            product_id=product.product_id,
            name=product.name,
            product_type=product.product_type,
            brand=product.brand,
            price=float(product.price) if product.price else None,
            currency=product.currency,
            availability_status=product.availability_status,
            image_url=product.image_url
        )
        for product in products
    ]


@products_router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a specific product by ID"""

    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return ProductResponse(
        id=product.id,
        product_id=product.product_id,
        trend_id=product.trend_id,
        name=product.name,
        product_type=product.product_type,
        description=product.description,
        brand=product.brand,
        price=float(product.price) if product.price else None,
        currency=product.currency,
        color=product.color,
        size=product.size,
        material=product.material,
        gender=product.gender,
        season=product.season,
        availability_status=product.availability_status,
        image_url=product.image_url,
        product_url=product.product_url,
        created_at=product.created_at,
        updated_at=product.updated_at
    )


@products_router.get("/stats/summary")
def get_product_stats(db: Session = Depends(get_db)):
    """Get product statistics"""

    total_count = db.query(func.count(Product.id)).scalar()

    # Get product type distribution
    product_types = db.query(
        Product.product_type,
        func.count(Product.id).label('count')
    ).group_by(Product.product_type).all()

    # Get brand distribution (top 10)
    brands = db.query(
        Product.brand,
        func.count(Product.id).label('count')
    ).filter(Product.brand.isnot(None)).group_by(Product.brand).order_by(
        func.count(Product.id).desc()
    ).limit(10).all()

    # Get availability distribution
    availability = db.query(
        Product.availability_status,
        func.count(Product.id).label('count')
    ).group_by(Product.availability_status).all()

    return {
        "total_products": total_count,
        "by_type": {ptype.product_type: ptype.count for ptype in product_types},
        "top_brands": {brand.brand: brand.count for brand in brands},
        "by_availability": {avail.availability_status: avail.count for avail in availability}
    }


@products_router.post("/bulk", response_model=ProductBulkUploadResponse)
def bulk_upload_products(
    request: ProductBulkUploadRequest,
    db: Session = Depends(get_db)
):
    """Bulk upload products from CSV data"""

    uploaded_count = 0
    skipped_count = 0
    error_count = 0
    errors = []

    try:
        for i, product_data in enumerate(request.products):
            try:
                # Generate product_id if not provided
                if not product_data.product_id:
                    # Create a simple product_id based on name and index
                    base_id = product_data.name.lower().replace(' ', '_')[:20]
                    product_data.product_id = f"{base_id}_{i+1:04d}"

                # Check if product already exists
                existing = db.query(Product).filter(
                    Product.product_id == product_data.product_id
                ).first()

                if existing:
                    skipped_count += 1
                    continue

                # Create new product
                new_product = Product(
                    product_id=product_data.product_id,
                    trend_id=product_data.trend_id,
                    name=product_data.name,
                    product_type=product_data.product_type,
                    description=product_data.description,
                    brand=product_data.brand,
                    price=product_data.price,
                    currency=product_data.currency,
                    color=product_data.color,
                    size=product_data.size,
                    material=product_data.material,
                    gender=product_data.gender,
                    season=product_data.season,
                    availability_status=product_data.availability_status,
                    image_url=product_data.image_url,
                    product_url=product_data.product_url
                )

                db.add(new_product)
                uploaded_count += 1

            except Exception as e:
                error_count += 1
                error_msg = f"Row {i+1}: {str(e)}"
                errors.append(error_msg)
                continue

        # Commit all changes
        db.commit()

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Bulk upload failed: {str(e)}"
        )

    return ProductBulkUploadResponse(
        uploaded_count=uploaded_count,
        skipped_count=skipped_count,
        error_count=error_count,
        errors=errors if errors else None
    )


@images_router.get("/stats/summary")
def get_image_stats(db: Session = Depends(get_db)):
    """Get image statistics"""

    stats = db.query(
        TrendImage.image_type,
        func.count(TrendImage.id).label('count')
    ).group_by(TrendImage.image_type).all()

    total_count = db.query(func.count(TrendImage.id)).scalar()

    return {
        "total_images": total_count,
        "by_type": {stat.image_type: stat.count for stat in stats}
    }