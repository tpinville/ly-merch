"""
Database configuration and session management
"""

import os
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from .models import Base

# Database configuration from environment
DB_URL = os.getenv("DB_URL", "mysql+pymysql://myapp:changeme_user@db:3306/myapp")

# Create engine with connection pooling
engine = create_engine(
    DB_URL,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600,   # Recycle connections after 1 hour
    future=True,
    echo=os.getenv("SQL_DEBUG", "").lower() == "true"  # Log SQL queries if SQL_DEBUG=true
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    This will be used as a FastAPI dependency.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Drop all tables from the database (use with caution!)"""
    Base.metadata.drop_all(bind=engine)


def test_connection() -> bool:
    """Test database connection"""
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False


# Health check function for database
def get_db_health() -> dict:
    """Get database health status"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT VERSION() as version, NOW() as server_time")).fetchone()

            # Get table counts
            table_counts = {}
            for table_name in ["verticals", "trends", "trend_images"]:
                try:
                    count_result = conn.execute(text(f"SELECT COUNT(*) as count FROM {table_name}")).fetchone()
                    table_counts[table_name] = count_result[0]
                except:
                    table_counts[table_name] = "error"

        return {
            "status": "healthy",
            "version": result[0],
            "server_time": str(result[1]),
            "table_counts": table_counts
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }