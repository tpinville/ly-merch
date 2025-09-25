"""
SQLAlchemy models for the fashion trends database
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from pydantic import BaseModel

Base = declarative_base()


class Vertical(Base):
    """Vertical model - main categories like sneakers, sandals, etc."""
    __tablename__ = "verticals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vertical_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    geo_zone: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    trends: Mapped[List["Trend"]] = relationship("Trend", back_populates="vertical", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Vertical(id={self.id}, name='{self.name}', geo_zone='{self.geo_zone}')>"


class Trend(Base):
    """Trend model - specific fashion trends within each vertical"""
    __tablename__ = "trends"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    trend_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    vertical_id: Mapped[int] = mapped_column(Integer, ForeignKey("verticals.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    image_hash: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    vertical: Mapped["Vertical"] = relationship("Vertical", back_populates="trends")
    images: Mapped[List["TrendImage"]] = relationship("TrendImage", back_populates="trend", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Trend(id={self.id}, name='{self.name}', vertical_id={self.vertical_id})>"


class TrendImage(Base):
    """TrendImage model - reference images for trends (positive/negative examples)"""
    __tablename__ = "trend_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    trend_id: Mapped[int] = mapped_column(Integer, ForeignKey("trends.id"), nullable=False)
    image_type: Mapped[str] = mapped_column(Enum("positive", "negative", name="image_type_enum"), nullable=False)
    md5_hash: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    trend: Mapped["Trend"] = relationship("Trend", back_populates="images")

    # Unique constraint for trend_id + md5_hash + image_type
    __table_args__ = (
        Index('unique_trend_image', 'trend_id', 'md5_hash', 'image_type', unique=True),
        Index('idx_trend_images_combined', 'trend_id', 'image_type'),
    )

    def __repr__(self):
        return f"<TrendImage(id={self.id}, trend_id={self.trend_id}, type='{self.image_type}', hash='{self.md5_hash}')>"


# Pydantic schemas for API serialization

class TrendImageResponse(BaseModel):
    """Response schema for trend images"""
    id: int
    image_type: str
    md5_hash: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TrendResponse(BaseModel):
    """Response schema for trends"""
    id: int
    trend_id: str
    name: str
    description: Optional[str] = None
    image_hash: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    images: Optional[List[TrendImageResponse]] = None

    class Config:
        from_attributes = True


class TrendSummaryResponse(BaseModel):
    """Summary response schema for trends (without images)"""
    id: int
    trend_id: str
    name: str
    description: Optional[str] = None
    image_hash: Optional[str] = None
    image_count: Optional[int] = 0
    positive_image_count: Optional[int] = 0
    negative_image_count: Optional[int] = 0

    class Config:
        from_attributes = True


class VerticalResponse(BaseModel):
    """Response schema for verticals"""
    id: int
    vertical_id: str
    name: str
    geo_zone: str
    created_at: datetime
    updated_at: datetime
    trends: Optional[List[TrendSummaryResponse]] = None
    trend_count: Optional[int] = 0

    class Config:
        from_attributes = True


class VerticalSummaryResponse(BaseModel):
    """Summary response schema for verticals (without trends)"""
    id: int
    vertical_id: str
    name: str
    geo_zone: str
    trend_count: int

    class Config:
        from_attributes = True


# Search/Filter schemas

class TrendSearchParams(BaseModel):
    """Parameters for searching trends"""
    query: Optional[str] = None
    vertical_id: Optional[int] = None
    vertical_name: Optional[str] = None
    geo_zone: Optional[str] = None
    has_images: Optional[bool] = None
    image_type: Optional[str] = None  # positive, negative
    limit: Optional[int] = 50
    offset: Optional[int] = 0


class VerticalSearchParams(BaseModel):
    """Parameters for searching verticals"""
    query: Optional[str] = None
    geo_zone: Optional[str] = None
    limit: Optional[int] = 50
    offset: Optional[int] = 0


class ImageSearchParams(BaseModel):
    """Parameters for searching images"""
    trend_id: Optional[int] = None
    image_type: Optional[str] = None  # positive, negative
    md5_hash: Optional[str] = None
    limit: Optional[int] = 50
    offset: Optional[int] = 0