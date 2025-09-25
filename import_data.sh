#!/bin/bash

# Script to import data from alls.json into MySQL database using Docker

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting data import from alls.json${NC}"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}Error: .env file not found!${NC}"
    exit 1
fi

# Source environment variables
source .env

# Check if alls.json exists
if [ ! -f frontend/alls.json ]; then
    echo -e "${RED}Error: frontend/alls.json file not found!${NC}"
    exit 1
fi

# Check if database container is running
if ! docker-compose ps db | grep -q "Up"; then
    echo -e "${YELLOW}Starting MySQL container...${NC}"
    docker-compose up -d db

    echo -e "${YELLOW}Waiting for MySQL to be ready...${NC}"
    while [ "$(docker-compose ps db | grep -c 'healthy')" -eq 0 ]; do
        echo "Waiting for MySQL container to be healthy..."
        sleep 2
    done
fi

echo -e "${GREEN}📖 Converting JSON to SQL...${NC}"

# Create a temporary Python script inside the container
docker-compose exec -T db bash -c "cat > /tmp/import_data.py" << 'EOF'
#!/usr/bin/env python3

import json
import re
import mysql.connector
import sys
import os

# Database connection
def get_connection():
    return mysql.connector.connect(
        host='localhost',
        user=os.environ.get('MYSQL_USER', 'myapp'),
        password=os.environ.get('MYSQL_PASSWORD', 'changeme_user'),
        database=os.environ.get('MYSQL_DATABASE', 'myapp'),
        charset='utf8mb4'
    )

def parse_json_file(content):
    """Parse multiple JSON objects from content"""
    json_objects_raw = re.split(r'}\s*{', content)

    if len(json_objects_raw) == 1:
        return [json.loads(content)]

    # Fix split objects
    json_objects_raw[0] += '}'
    for i in range(1, len(json_objects_raw)-1):
        json_objects_raw[i] = '{' + json_objects_raw[i] + '}'
    json_objects_raw[-1] = '{' + json_objects_raw[-1]

    parsed = []
    for obj_str in json_objects_raw:
        try:
            parsed.append(json.loads(obj_str))
        except json.JSONDecodeError as e:
            print(f"Warning: Skipping invalid JSON: {e}")

    return parsed

def clear_data(cursor):
    """Clear existing data"""
    print("🗑️ Clearing existing data...")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    for table in ['trend_images', 'trends', 'verticals']:
        cursor.execute(f"TRUNCATE TABLE {table}")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

def main():
    # Read JSON from stdin
    content = sys.stdin.read()

    try:
        json_objects = parse_json_file(content)
        print(f"📋 Found {len(json_objects)} JSON objects")

        conn = get_connection()
        cursor = conn.cursor()

        clear_data(cursor)

        total_verticals = 0
        total_trends = 0
        total_images = 0

        for obj in json_objects:
            verticals = obj.get('verticals', [])

            for vertical in verticals:
                # Insert vertical
                cursor.execute("""
                    INSERT INTO verticals (vertical_id, name, geo_zone)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE name = VALUES(name)
                """, (vertical['vertical_id'], vertical['name'], vertical['geo_zone']))

                cursor.execute("SELECT LAST_INSERT_ID()")
                vertical_db_id = cursor.fetchone()[0]
                if vertical_db_id == 0:
                    cursor.execute("SELECT id FROM verticals WHERE vertical_id = %s",
                                 (vertical['vertical_id'],))
                    vertical_db_id = cursor.fetchone()[0]

                total_verticals += 1
                print(f"📁 {vertical['name']}")

                for trend in vertical.get('trends', []):
                    # Insert trend
                    cursor.execute("""
                        INSERT INTO trends (trend_id, vertical_id, name, description, image_hash)
                        VALUES (%s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE name = VALUES(name)
                    """, (trend['trend_id'], vertical_db_id, trend['name'],
                         trend.get('description', ''), trend.get('image', '')))

                    cursor.execute("SELECT LAST_INSERT_ID()")
                    trend_db_id = cursor.fetchone()[0]
                    if trend_db_id == 0:
                        cursor.execute("SELECT id FROM trends WHERE trend_id = %s",
                                     (trend['trend_id'],))
                        trend_db_id = cursor.fetchone()[0]

                    total_trends += 1

                    # Insert images
                    for img in trend.get('positive_images', []):
                        cursor.execute("""
                            INSERT INTO trend_images (trend_id, image_type, md5_hash, description)
                            VALUES (%s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE description = VALUES(description)
                        """, (trend_db_id, 'positive', img['md5'], img.get('description', '')))
                        total_images += 1

                    for img in trend.get('negative_images', []):
                        cursor.execute("""
                            INSERT INTO trend_images (trend_id, image_type, md5_hash, description)
                            VALUES (%s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE description = VALUES(description)
                        """, (trend_db_id, 'negative', img['md5'], img.get('description', '')))
                        total_images += 1

        conn.commit()

        print(f"\n🎉 Import completed!")
        print(f"📊 Imported: {total_verticals} verticals, {total_trends} trends, {total_images} images")

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    finally:
        cursor.close()
        conn.close()

    return 0

if __name__ == "__main__":
    exit(main())
EOF

# Copy the JSON file to the container and run the import
echo -e "${YELLOW}📥 Importing data...${NC}"

docker-compose exec -T db bash -c "
    export MYSQL_USER='${MYSQL_USER}'
    export MYSQL_PASSWORD='${MYSQL_PASSWORD}'
    export MYSQL_DATABASE='${MYSQL_DATABASE}'
    python3 /tmp/import_data.py
" < frontend/alls.json

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Data import completed successfully!${NC}"

    # Show summary
    echo -e "\n${YELLOW}📊 Database summary:${NC}"
    docker-compose exec -T db mysql -h localhost -u"${MYSQL_USER}" -p"${MYSQL_PASSWORD}" "${MYSQL_DATABASE}" -e "
        SELECT 'verticals' as table_name, COUNT(*) as count FROM verticals
        UNION ALL
        SELECT 'trends' as table_name, COUNT(*) as count FROM trends
        UNION ALL
        SELECT 'trend_images' as table_name, COUNT(*) as count FROM trend_images;
    "

    echo -e "\n${GREEN}🎯 Sample data:${NC}"
    docker-compose exec -T db mysql -h localhost -u"${MYSQL_USER}" -p"${MYSQL_PASSWORD}" "${MYSQL_DATABASE}" -e "
        SELECT v.name as vertical, COUNT(t.id) as trends
        FROM verticals v
        LEFT JOIN trends t ON v.id = t.vertical_id
        GROUP BY v.id, v.name
        ORDER BY trends DESC
        LIMIT 5;
    "
else
    echo -e "${RED}❌ Data import failed${NC}"
    exit 1
fi

echo -e "\n${GREEN}✅ All done! You can now query your data.${NC}"