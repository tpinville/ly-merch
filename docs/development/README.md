# 🛠️ Development Setup Guide

This guide covers setting up the LY-Merch platform for local development.

## 📋 Prerequisites

### Required Software
- **Docker & Docker Compose** (Recommended for full setup)
- **Node.js 18+** (for frontend development)
- **Python 3.9+** (for backend development)
- **Git** (for version control)

### Optional Tools
- **MySQL 8.0+** (if not using Docker)
- **nginx** (if not using Docker)
- **VS Code** with extensions for Python, TypeScript, and Docker

## 🐳 Docker Setup (Recommended)

### Full Stack with Docker
```bash
# Clone the repository
git clone <repository-url>
cd ly-merch

# Start all services
docker-compose up -d

# Verify services are running
docker-compose ps

# View logs
docker-compose logs -f api
docker-compose logs -f frontend
```

### Services Overview
- **frontend**: React app on port 8080
- **api**: FastAPI backend on port 8001
- **db**: MySQL database on port 3307
- **nginx**: Reverse proxy on port 8080

## 💻 Local Development

### Backend API Development

```bash
cd api

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your database settings

# Start development server
uvicorn app.main:app --reload --port 8001

# API will be available at http://localhost:8001
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Frontend will be available at http://localhost:5173
```

### Database Setup

#### Using Docker (Recommended)
```bash
# Start MySQL container only
docker-compose up -d db

# Access MySQL CLI
docker-compose exec db mysql -u myapp -p myapp
```

#### Local MySQL Setup
```bash
# Install MySQL 8.0+
# Create database and user
mysql -u root -p
```

```sql
CREATE DATABASE myapp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'myapp'@'localhost' IDENTIFIED BY 'changeme_user';
GRANT ALL PRIVILEGES ON myapp.* TO 'myapp'@'localhost';
FLUSH PRIVILEGES;
```

## 📊 Database Operations

### Initialize Database
```bash
cd scripts

# Import sample data
./import_data.sh

# Or use Python script
python3 import_data.py
```

### Sample Data
The repository includes comprehensive sample data:
- 15 categories (sneakers, sandals, boots, etc.)
- 105 verticals (brand-specific categories)
- 440+ trends (fashion trend data)
- 248+ images (trend reference images)

### Test Data Upload
```bash
cd scripts

# Test CSV product upload
python3 upload_csv_test.py

# Verify upload
curl http://localhost:8001/api/v1/products?limit=5
```

## 🔧 Development Commands

### Docker Commands
```bash
# Build and start
docker-compose up --build

# Stop all services
docker-compose down

# Restart specific service
docker-compose restart api

# View service logs
docker-compose logs -f api

# Execute commands in containers
docker-compose exec api python -c "print('Hello from API')"
docker-compose exec db mysql -u myapp -p myapp

# Clean up
docker-compose down -v  # Remove volumes
docker system prune     # Clean up Docker
```

### Backend Commands
```bash
cd api

# Run tests
python -m pytest

# Format code
black app/
isort app/

# Lint code
flake8 app/

# Database migration (when implemented)
alembic upgrade head
```

### Frontend Commands
```bash
cd frontend

# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint and format
npm run lint
npm run format

# Type checking
npm run type-check
```

## 📁 Project Structure Details

```
ly-merch/
├── api/                    # FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py        # FastAPI app initialization
│   │   ├── database.py    # Database connection
│   │   ├── models.py      # SQLAlchemy models
│   │   ├── schemas.py     # Pydantic schemas
│   │   └── routers.py     # API endpoints
│   ├── requirements.txt   # Python dependencies
│   └── Dockerfile
│
├── frontend/              # React application
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/        # Page components
│   │   ├── hooks/        # Custom hooks
│   │   ├── utils/        # Utility functions
│   │   └── types/        # TypeScript types
│   ├── package.json      # Node dependencies
│   ├── vite.config.ts    # Vite configuration
│   └── Dockerfile
│
├── data/                 # Sample data files
│   ├── alls.json        # Trend and vertical data
│   ├── sample_products.csv
│   └── test_products_edge_cases.csv
│
├── scripts/              # Utility scripts
│   ├── import_data.py   # Database import script
│   ├── upload_csv_test.py
│   └── import_data.sh
│
├── docs/                # Documentation
└── docker-compose.yml  # Multi-service setup
```

## 🔍 Debugging

### Common Issues

#### Database Connection Failed
```bash
# Check if database is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Verify connection settings in .env
cat .env

# Test connection
python3 -c "from api.app.database import test_connection; print(test_connection())"
```

#### Frontend API Errors
```bash
# Check API is running
curl http://localhost:8001/health

# Check nginx proxy (if using Docker)
docker-compose logs nginx

# Verify API calls in browser dev tools
```

#### Port Conflicts
```bash
# Check what's using ports
lsof -i :8080  # Frontend
lsof -i :8001  # API
lsof -i :3307  # Database

# Stop conflicting services
docker-compose down
```

### Development Tools

#### API Testing
```bash
# Test API endpoints
curl http://localhost:8001/docs  # Swagger UI
curl http://localhost:8001/api/v1/products

# Use httpie for better formatting
pip install httpie
http GET localhost:8001/api/v1/products
```

#### Database Inspection
```bash
# Access database
docker-compose exec db mysql -u myapp -p myapp

# Common queries
SELECT COUNT(*) FROM products;
SELECT * FROM categories;
SHOW TABLES;
DESCRIBE products;
```

## 🧪 Testing

### Backend Tests
```bash
cd api

# Install test dependencies
pip install pytest pytest-cov

# Run tests
python -m pytest

# Run with coverage
python -m pytest --cov=app

# Run specific test file
python -m pytest tests/test_products.py
```

### Frontend Tests
```bash
cd frontend

# Install test dependencies
npm install --save-dev @testing-library/react @testing-library/jest-dom

# Run tests
npm test

# Run with coverage
npm run test:coverage
```

### Integration Tests
```bash
# Full system test
cd scripts
python3 upload_csv_test.py

# API endpoint tests
curl -X POST http://localhost:8001/api/v1/products/bulk \
  -H "Content-Type: application/json" \
  -d @../data/sample_products.json
```

## 🚀 Production Preparation

### Environment Variables
```bash
# Copy environment template
cp .env.example .env

# Required variables
MYSQL_ROOT_PASSWORD=secure_root_password
MYSQL_PASSWORD=secure_user_password
MYSQL_USER=myapp
MYSQL_DATABASE=myapp
```

### Build Production Images
```bash
# Build all services
docker-compose -f docker-compose.prod.yml build

# Run production stack
docker-compose -f docker-compose.prod.yml up -d
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Vite Documentation](https://vitejs.dev/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)