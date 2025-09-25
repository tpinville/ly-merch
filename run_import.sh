#!/bin/bash

# Script to execute the generated SQL import file

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Importing data to MySQL database${NC}"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}Error: .env file not found!${NC}"
    exit 1
fi

# Source environment variables
source .env

# Generate SQL file first
echo -e "${YELLOW}📝 Generating SQL statements...${NC}"
python3 import_simple.py

if [ ! -f import_data.sql ]; then
    echo -e "${RED}Error: import_data.sql not generated!${NC}"
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

echo -e "${YELLOW}📥 Executing SQL import...${NC}"

# Import the SQL file
docker-compose exec -T db mysql -h localhost -u"${MYSQL_USER}" -p"${MYSQL_PASSWORD}" "${MYSQL_DATABASE}" < import_data.sql

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

    echo -e "\n${GREEN}🎯 Sample data (top verticals by trend count):${NC}"
    docker-compose exec -T db mysql -h localhost -u"${MYSQL_USER}" -p"${MYSQL_PASSWORD}" "${MYSQL_DATABASE}" -e "
        SELECT v.name as vertical, COUNT(t.id) as trends
        FROM verticals v
        LEFT JOIN trends t ON v.id = t.vertical_id
        GROUP BY v.id, v.name
        ORDER BY trends DESC
        LIMIT 5;
    "

    echo -e "\n${GREEN}🖼️ Image type distribution:${NC}"
    docker-compose exec -T db mysql -h localhost -u"${MYSQL_USER}" -p"${MYSQL_PASSWORD}" "${MYSQL_DATABASE}" -e "
        SELECT image_type, COUNT(*) as count
        FROM trend_images
        GROUP BY image_type;
    "
else
    echo -e "${RED}❌ Data import failed${NC}"
    exit 1
fi

echo -e "\n${GREEN}✅ Import complete! Access your data at:${NC}"
echo -e "${YELLOW}• MySQL: localhost:3307${NC}"
echo -e "${YELLOW}• Adminer: http://localhost:8081${NC}"