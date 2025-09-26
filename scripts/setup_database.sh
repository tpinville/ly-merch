#!/bin/bash

# Database setup script for MySQL Docker container
# Reads configuration from .env file and applies schema.sql

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up MySQL database...${NC}"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}Error: .env file not found!${NC}"
    exit 1
fi

# Source environment variables
source .env

# Check if schema.sql exists
if [ ! -f schema.sql ]; then
    echo -e "${RED}Error: schema.sql file not found!${NC}"
    exit 1
fi

# Check if docker-compose is running
if ! docker-compose ps db | grep -q "Up"; then
    echo -e "${YELLOW}Starting MySQL container...${NC}"
    docker-compose up -d db

    echo -e "${YELLOW}Waiting for MySQL to be ready...${NC}"
    # Wait for MySQL to be healthy
    while [ "$(docker-compose ps db | grep -c 'healthy')" -eq 0 ]; do
        echo "Waiting for MySQL container to be healthy..."
        sleep 2
    done
    echo -e "${GREEN}MySQL container is ready!${NC}"
else
    echo -e "${GREEN}MySQL container is already running${NC}"
fi

# Execute the schema
echo -e "${YELLOW}Applying database schema...${NC}"

# Use mysql client from the docker container to execute the schema
docker-compose exec -T db mysql -h localhost -u"${MYSQL_USER}" -p"${MYSQL_PASSWORD}" "${MYSQL_DATABASE}" < schema.sql

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Database schema applied successfully!${NC}"
    echo -e "${GREEN}✓ Database: ${MYSQL_DATABASE}${NC}"
    echo -e "${GREEN}✓ User: ${MYSQL_USER}${NC}"
    echo -e "${GREEN}✓ Host: localhost:3307${NC}"
    echo -e "${YELLOW}You can access Adminer at: http://localhost:8081${NC}"
else
    echo -e "${RED}✗ Failed to apply database schema${NC}"
    exit 1
fi

# Show database info
echo -e "\n${YELLOW}Database tables created:${NC}"
docker-compose exec -T db mysql -h localhost -u"${MYSQL_USER}" -p"${MYSQL_PASSWORD}" "${MYSQL_DATABASE}" -e "SHOW TABLES;"

echo -e "\n${GREEN}Database setup complete!${NC}"