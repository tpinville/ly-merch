#!/usr/bin/env python3
"""
Script to import data from alls.json into MySQL database
"""

import json
import re
import os
import mysql.connector
from typing import List, Dict, Any

# Database configuration from environment
DB_CONFIG = {
    'host': 'localhost',
    'port': 3307,
    'user': os.getenv('MYSQL_USER', 'myapp'),
    'password': os.getenv('MYSQL_PASSWORD', 'changeme_user'),
    'database': os.getenv('MYSQL_DATABASE', 'myapp'),
    'charset': 'utf8mb4',
    'autocommit': False
}

def load_env_file():
    """Load environment variables from .env file"""
    try:
        with open('.env', 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    except FileNotFoundError:
        print("Warning: .env file not found, using defaults")

def parse_json_objects(file_path: str) -> List[Dict[Any, Any]]:
    """Parse multiple JSON objects from the file"""
    print(f"📖 Reading {file_path}...")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split content by '}{'  pattern to find separate JSON objects
    json_objects_raw = re.split(r'}\s*{', content)
    print(f"Found {len(json_objects_raw)} JSON objects")

    # Fix the split objects by adding back braces
    json_objects = []
    if len(json_objects_raw) > 1:
        json_objects_raw[0] += '}'
        for i in range(1, len(json_objects_raw)-1):
            json_objects_raw[i] = '{' + json_objects_raw[i] + '}'
        json_objects_raw[-1] = '{' + json_objects_raw[-1]

    # Parse each JSON object
    parsed_objects = []
    for i, obj_str in enumerate(json_objects_raw):
        try:
            obj = json.loads(obj_str)
            parsed_objects.append(obj)
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing JSON object {i+1}: {e}")
            continue

    print(f"✅ Successfully parsed {len(parsed_objects)} JSON objects")
    return parsed_objects

def get_db_connection():
    """Get MySQL database connection"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        print("✅ Connected to MySQL database")
        return conn
    except mysql.connector.Error as e:
        print(f"❌ Error connecting to MySQL: {e}")
        raise

def clear_existing_data(cursor):
    """Clear existing data from tables"""
    print("🗑️ Clearing existing data...")

    # Disable foreign key checks temporarily
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

    tables = ['trend_images', 'trends', 'verticals']
    for table in tables:
        cursor.execute(f"TRUNCATE TABLE {table}")
        print(f"  Cleared {table}")

    # Re-enable foreign key checks
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

def insert_vertical(cursor, vertical_data: Dict) -> int:
    """Insert a vertical and return its database ID"""
    insert_query = """
        INSERT INTO verticals (vertical_id, name, geo_zone)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
        name = VALUES(name), geo_zone = VALUES(geo_zone)
    """

    cursor.execute(insert_query, (
        vertical_data['vertical_id'],
        vertical_data['name'],
        vertical_data['geo_zone']
    ))

    # Get the ID of the inserted/updated vertical
    cursor.execute("SELECT id FROM verticals WHERE vertical_id = %s",
                  (vertical_data['vertical_id'],))
    return cursor.fetchone()[0]

def insert_trend(cursor, trend_data: Dict, vertical_db_id: int) -> int:
    """Insert a trend and return its database ID"""
    insert_query = """
        INSERT INTO trends (trend_id, vertical_id, name, description, image_hash)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        name = VALUES(name), description = VALUES(description),
        image_hash = VALUES(image_hash)
    """

    cursor.execute(insert_query, (
        trend_data['trend_id'],
        vertical_db_id,
        trend_data['name'],
        trend_data.get('description', ''),
        trend_data.get('image', '')
    ))

    # Get the ID of the inserted/updated trend
    cursor.execute("SELECT id FROM trends WHERE trend_id = %s",
                  (trend_data['trend_id'],))
    return cursor.fetchone()[0]

def insert_images(cursor, images: List[Dict], trend_db_id: int, image_type: str):
    """Insert images for a trend"""
    if not images:
        return

    insert_query = """
        INSERT INTO trend_images (trend_id, image_type, md5_hash, description)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE description = VALUES(description)
    """

    for image in images:
        cursor.execute(insert_query, (
            trend_db_id,
            image_type,
            image['md5'],
            image.get('description', '')
        ))

def import_data(json_objects: List[Dict]):
    """Import all data into the database"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Clear existing data
        clear_existing_data(cursor)
        conn.commit()

        total_verticals = 0
        total_trends = 0
        total_images = 0

        print("📥 Importing data...")

        for obj_idx, json_obj in enumerate(json_objects):
            print(f"\n🔄 Processing JSON object {obj_idx + 1}/{len(json_objects)}")

            verticals = json_obj.get('verticals', [])

            for vertical in verticals:
                # Insert vertical
                vertical_db_id = insert_vertical(cursor, vertical)
                total_verticals += 1
                print(f"  📁 Vertical: {vertical['name']} ({vertical['vertical_id']})")

                trends = vertical.get('trends', [])

                for trend in trends:
                    # Insert trend
                    trend_db_id = insert_trend(cursor, trend, vertical_db_id)
                    total_trends += 1
                    print(f"    🏷️  Trend: {trend['name']}")

                    # Insert positive images
                    positive_images = trend.get('positive_images', [])
                    insert_images(cursor, positive_images, trend_db_id, 'positive')
                    total_images += len(positive_images)

                    # Insert negative images
                    negative_images = trend.get('negative_images', [])
                    insert_images(cursor, negative_images, trend_db_id, 'negative')
                    total_images += len(negative_images)

                    if positive_images or negative_images:
                        print(f"      🖼️  Images: {len(positive_images)} positive, {len(negative_images)} negative")

        # Commit all changes
        conn.commit()

        print(f"\n🎉 Import completed successfully!")
        print(f"📊 Summary:")
        print(f"  • Verticals: {total_verticals}")
        print(f"  • Trends: {total_trends}")
        print(f"  • Images: {total_images}")

    except Exception as e:
        conn.rollback()
        print(f"❌ Error during import: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

def verify_import(conn):
    """Verify the imported data"""
    cursor = conn.cursor()

    print("\n🔍 Verifying imported data...")

    # Count records in each table
    tables = {
        'verticals': 'SELECT COUNT(*) FROM verticals',
        'trends': 'SELECT COUNT(*) FROM trends',
        'trend_images': 'SELECT COUNT(*) FROM trend_images'
    }

    for table, query in tables.items():
        cursor.execute(query)
        count = cursor.fetchone()[0]
        print(f"  {table}: {count} records")

    # Show some sample data
    cursor.execute("""
        SELECT v.name as vertical, t.name as trend,
               COUNT(ti.id) as image_count
        FROM verticals v
        JOIN trends t ON v.id = t.vertical_id
        LEFT JOIN trend_images ti ON t.id = ti.trend_id
        GROUP BY v.id, t.id
        ORDER BY v.name, t.name
        LIMIT 5
    """)

    print("\n📋 Sample data:")
    for row in cursor.fetchall():
        print(f"  {row[0]} > {row[1]} ({row[2]} images)")

    cursor.close()

def main():
    """Main function"""
    print("🚀 Starting data import from alls.json")

    # Load environment variables
    load_env_file()

    # Update DB config with loaded env vars
    DB_CONFIG.update({
        'user': os.getenv('MYSQL_USER', 'myapp'),
        'password': os.getenv('MYSQL_PASSWORD', 'changeme_user'),
        'database': os.getenv('MYSQL_DATABASE', 'myapp')
    })

    try:
        # Parse JSON data
        json_objects = parse_json_objects('frontend/alls.json')

        if not json_objects:
            print("❌ No valid JSON objects found")
            return

        # Import data
        import_data(json_objects)

        # Verify import
        conn = get_db_connection()
        verify_import(conn)
        conn.close()

        print("\n✅ Data import completed successfully!")

    except Exception as e:
        print(f"❌ Import failed: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())