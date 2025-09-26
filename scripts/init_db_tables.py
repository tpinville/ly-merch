#!/usr/bin/env python3
"""
Initialize database tables using SQLAlchemy models
"""

import os
import sys

# Add the API app to path
sys.path.append('/home/tony/dev/ly-merch/api')

try:
    from app.database import engine, create_tables, test_connection
    from app.models import Base

    print("🔧 Testing database connection...")
    if not test_connection():
        print("❌ Database connection failed")
        exit(1)

    print("✅ Database connection successful")

    print("🔧 Creating tables...")
    create_tables()
    print("✅ Tables created successfully")

    # Verify tables exist
    from sqlalchemy import text
    with engine.connect() as conn:
        result = conn.execute(text("SHOW TABLES")).fetchall()
        tables = [row[0] for row in result]
        print(f"📋 Tables in database: {', '.join(tables)}")

        # Check if products table has the right structure
        if 'products' in tables:
            result = conn.execute(text("DESCRIBE products")).fetchall()
            print(f"📋 Products table structure:")
            for row in result[:10]:  # Show first 10 columns
                print(f"   {row[0]} - {row[1]}")
            if len(result) > 10:
                print(f"   ... and {len(result) - 10} more columns")

    print("🎉 Database initialization complete!")

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the project root directory")
    exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)