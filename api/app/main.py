import os
from typing import List
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import get_db, get_db_health
from .routers import verticals_router, trends_router, images_router

API_LOG_LEVEL = os.getenv("API_LOG_LEVEL", "info")
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]

app = FastAPI(
    title="Fashion Trends API",
    description="API for accessing fashion trends and vertical data",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

if CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.get("/health")
def health():
    """Health check endpoint with database status"""
    db_health = get_db_health()
    return {
        "status": "ok",
        "api_version": "1.0.0",
        "database": db_health
    }

# Include API routers
app.include_router(verticals_router, prefix="/api/v1")
app.include_router(trends_router, prefix="/api/v1")
app.include_router(images_router, prefix="/api/v1")


@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "message": "Fashion Trends API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "verticals": "/api/v1/verticals",
            "trends": "/api/v1/trends",
            "images": "/api/v1/images",
            "health": "/health"
        }
    }


@app.get("/api/v1/stats")
def get_api_stats(db: Session = Depends(get_db)):
    """Get overall API statistics"""
    from sqlalchemy import func
    from .models import Vertical, Trend, TrendImage

    vertical_count = db.query(func.count(Vertical.id)).scalar()
    trend_count = db.query(func.count(Trend.id)).scalar()
    image_count = db.query(func.count(TrendImage.id)).scalar()

    # Get geo zone distribution
    geo_zones = db.query(
        Vertical.geo_zone,
        func.count(Vertical.id).label('count')
    ).group_by(Vertical.geo_zone).all()

    # Get image type distribution
    image_types = db.query(
        TrendImage.image_type,
        func.count(TrendImage.id).label('count')
    ).group_by(TrendImage.image_type).all()

    return {
        "total_verticals": vertical_count,
        "total_trends": trend_count,
        "total_images": image_count,
        "geo_zones": {zone.geo_zone: zone.count for zone in geo_zones},
        "image_types": {img_type.image_type: img_type.count for img_type in image_types}
    }
