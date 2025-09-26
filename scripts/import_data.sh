#!/bin/bash

# Script to import data from alls.json into MySQL database using Docker

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting data import from alls.json${NC}"

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to project root
cd "$PROJECT_ROOT"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}Error: .env file not found in $PROJECT_ROOT!${NC}"
    echo -e "${YELLOW}Please run this script from the project root or ensure .env exists${NC}"
    exit 1
fi

# Source environment variables
source .env

# Check if alls.json exists
DATA_FILE="$PROJECT_ROOT/data/alls.json"
if [ ! -f "$DATA_FILE" ]; then
    echo -e "${RED}Error: $DATA_FILE file not found!${NC}"
    exit 1
fi

echo -e "${BLUE}ℹ️  Using data file: $DATA_FILE${NC}"

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

# Check if API container is running
if ! docker-compose ps api | grep -q "Up"; then
    echo -e "${YELLOW}Starting API container...${NC}"
    docker-compose up -d api

    echo -e "${YELLOW}Waiting for API to be ready...${NC}"
    sleep 5
fi

echo -e "${GREEN}📖 Converting JSON to SQL...${NC}"

# Copy the JSON file to the API container and run the import
echo -e "${YELLOW}📥 Importing data...${NC}"

# Copy data file to API container
docker-compose exec -T api mkdir -p /data
docker cp "$DATA_FILE" "$(docker-compose ps -q api):/data/alls.json"

# Run the import using the full-setup script's working Python approach
docker-compose exec -T api bash -c "
export MYSQL_USER='${MYSQL_USER}'
export MYSQL_PASSWORD='${MYSQL_PASSWORD}'
export MYSQL_DATABASE='${MYSQL_DATABASE}'

python3 << 'EOF'
#!/usr/bin/env python3

import json
import re
import os
import sys

# Add the app directory to Python path
sys.path.append('/app')

# Import SQLAlchemy models
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.models import Category, Vertical, Trend, TrendImage

# Database connection
def get_engine():
    user = os.environ.get('MYSQL_USER', 'myapp')
    password = os.environ.get('MYSQL_PASSWORD', 'changeme_user')
    database = os.environ.get('MYSQL_DATABASE', 'myapp')
    return create_engine(f'mysql+pymysql://{user}:{password}@db:3306/{database}')

def parse_json_file(content):
    # Handle multiple JSON objects separated by }{ pattern
    json_objects_raw = re.split(r'}\s*{', content)

    if len(json_objects_raw) == 1:
        return [json.loads(content)]

    # Fix split objects by adding missing braces
    json_objects_raw[0] += '}'
    for i in range(1, len(json_objects_raw)-1):
        json_objects_raw[i] = '{' + json_objects_raw[i] + '}'
    json_objects_raw[-1] = '{' + json_objects_raw[-1]

    parsed = []
    for obj_str in json_objects_raw:
        try:
            parsed.append(json.loads(obj_str))
        except json.JSONDecodeError as e:
            print(f'Warning: Skipping invalid JSON: {e}')

    return parsed

try:
    # Read JSON file
    print('📖 Reading /data/alls.json...')
    with open('/data/alls.json', 'r', encoding='utf-8') as f:
        content = f.read()

    json_objects = parse_json_file(content)
    print(f'Found {len(json_objects)} JSON objects')
    print('✅ Successfully parsed {len(json_objects)} JSON objects')

    # Create database session
    engine = get_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()

    # Clear existing data
    print('🗑️ Clearing existing data...')
    session.execute(text('SET FOREIGN_KEY_CHECKS = 0'))
    session.execute(text('TRUNCATE TABLE trend_images'))
    session.execute(text('TRUNCATE TABLE trends'))
    session.execute(text('TRUNCATE TABLE verticals'))
    session.execute(text('TRUNCATE TABLE categories'))
    session.execute(text('SET FOREIGN_KEY_CHECKS = 1'))
    session.commit()

    total_categories = 0
    total_verticals = 0
    total_trends = 0
    total_images = 0
    processed_categories = set()

    # Process each JSON object
    for i, obj in enumerate(json_objects):
        if (i + 1) % 3 == 0:
            print(f'🔄 Processing JSON object {i+1}/{len(json_objects)}')

        verticals = obj.get('verticals', [])

        for vertical in verticals:
            # Extract category from vertical_id
            vertical_id = vertical['vertical_id']
            category_name = vertical_id.split(':')[0] if ':' in vertical_id else 'uncategorized'

            # Create category if not exists
            if category_name not in processed_categories:
                category = session.query(Category).filter(Category.name == category_name).first()
                if not category:
                    category = Category(
                        name=category_name,
                        description=f'Category for {category_name} products'
                    )
                    session.add(category)
                    session.flush()  # Get the ID
                    total_categories += 1
                processed_categories.add(category_name)
            else:
                category = session.query(Category).filter(Category.name == category_name).first()

            # Create or get vertical
            db_vertical = session.query(Vertical).filter(Vertical.vertical_id == vertical['vertical_id']).first()
            if not db_vertical:
                db_vertical = Vertical(
                    vertical_id=vertical['vertical_id'],
                    category_id=category.id,
                    name=vertical['name'],
                    geo_zone=vertical['geo_zone']
                )
                session.add(db_vertical)
                session.flush()
                total_verticals += 1

            # Process trends
            for trend in vertical.get('trends', []):
                db_trend = session.query(Trend).filter(Trend.trend_id == trend['trend_id']).first()
                if not db_trend:
                    db_trend = Trend(
                        trend_id=trend['trend_id'],
                        vertical_id=db_vertical.id,
                        name=trend['name'],
                        description=trend.get('description', ''),
                        image_hash=trend.get('image', '')
                    )
                    session.add(db_trend)
                    session.flush()
                    total_trends += 1

                # Add images
                for img in trend.get('positive_images', []):
                    db_image = TrendImage(
                        trend_id=db_trend.id,
                        image_type='positive',
                        md5_hash=img['md5'],
                        description=img.get('description', '')
                    )
                    session.add(db_image)
                    total_images += 1

                for img in trend.get('negative_images', []):
                    db_image = TrendImage(
                        trend_id=db_trend.id,
                        image_type='negative',
                        md5_hash=img['md5'],
                        description=img.get('description', '')
                    )
                    session.add(db_image)
                    total_images += 1

    # Commit all changes
    session.commit()

    print('🎉 Import completed successfully!')
    print(f'📊 Summary:')
    print(f'  • Categories: {total_categories}')
    print(f'  • Verticals: {total_verticals}')
    print(f'  • Trends: {total_trends}')
    print(f'  • Images: {total_images}')

    # Final verification
    print('🔍 Verifying final counts...')
    with engine.connect() as conn:
        category_count = conn.execute(text('SELECT COUNT(*) FROM categories')).scalar()
        vertical_count = conn.execute(text('SELECT COUNT(*) FROM verticals')).scalar()
        trend_count = conn.execute(text('SELECT COUNT(*) FROM trends')).scalar()
        image_count = conn.execute(text('SELECT COUNT(*) FROM trend_images')).scalar()

        print(f'  categories: {category_count}')
        print(f'  verticals: {vertical_count}')
        print(f'  trends: {trend_count}')
        print(f'  trend_images: {image_count}')

        if category_count > 0 and vertical_count > 0 and trend_count > 0:
            print('✅ Data import verification successful!')
        else:
            print('❌ Data import verification failed!')
            exit(1)

except Exception as e:
    print(f'❌ Import failed: {e}')
    if session:
        session.rollback()
    exit(1)
finally:
    if session:
        session.close()
EOF
"

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