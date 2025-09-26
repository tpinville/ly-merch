# 👗 LY-Merch Fashion Trends Platform

A full-stack fashion trends analysis and product management platform built with FastAPI, React, and MySQL.

![Project Status](https://img.shields.io/badge/Status-Active%20Development-green)
![Python](https://img.shields.io/badge/Python-3.9+-blue)
![React](https://img.shields.io/badge/React-18+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-blue)

## 🎯 Overview

LY-Merch is a comprehensive platform for analyzing fashion trends and managing product catalogs. It provides tools for trend discovery, product classification, and data-driven fashion insights.

### ✨ Key Features

- **📈 Trend Analysis**: Import and analyze fashion trend data from multiple sources
- **🏷️ Product Management**: Comprehensive product catalog with categories, brands, and pricing
- **📊 Data Visualization**: Interactive dashboards for trend and product insights
- **📤 Bulk Operations**: CSV import/export for efficient data management
- **🔍 Advanced Search**: Filter products by type, brand, price, availability
- **🏗️ Hierarchical Data**: Categories → Verticals → Trends → Products structure

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for local development)
- Python 3.9+ (for local development)

### 🐳 Run with Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd ly-merch

# Start all services
docker-compose up -d

# Access the application
open http://localhost:8080
```

### 🛠️ Local Development

```bash
# Backend API
cd api
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001

# Frontend
cd frontend
npm install
npm run dev

# Database
docker-compose up -d db
```

## 📁 Project Structure

```
ly-merch/
├── 📚 docs/                    # Documentation
├── 🎨 frontend/               # React application
├── ⚙️ api/                    # FastAPI backend
├── 📊 data/                   # Sample data & CSV files
├── 🔧 scripts/                # Utility scripts
├── 🏗️ infra/                  # Docker configurations
└── 📋 Root configuration files
```

## 🏗️ Architecture

### Tech Stack
- **Frontend**: React 18, TypeScript, Vite
- **Backend**: FastAPI, SQLAlchemy, Pydantic
- **Database**: MySQL 8.0
- **Infrastructure**: Docker, Nginx
- **Development**: Hot reload, auto-restart

### Data Model
```
Categories (sneakers, boots, sandals)
    ↓
Verticals (brand-specific categories)
    ↓
Trends (specific fashion trends)
    ↓
Products (actual items for sale)
    ↓
Images (product/trend images)
```

## 📖 Documentation

- **[API Documentation](docs/api/)** - REST API endpoints and schemas
- **[Development Setup](docs/development/)** - Local development guide
- **[Deployment Guide](docs/deployment/)** - Production deployment
- **[Data Import](scripts/)** - CSV import and data management

## 🚀 Usage Examples

### Import Product Data
```bash
# Using the bulk upload UI
1. Navigate to "Bulk Upload" in the dashboard
2. Drag & drop your CSV file
3. Review validation results
4. Click "Upload Products"

# Using scripts
cd scripts
python upload_csv_test.py
```

### API Usage
```bash
# Get all products
curl http://localhost:8001/api/v1/products

# Filter by category
curl http://localhost:8001/api/v1/products?category_name=sneakers

# Bulk upload products
curl -X POST http://localhost:8001/api/v1/products/bulk \
  -H "Content-Type: application/json" \
  -d @data/sample_products.json
```

## 🗄️ Database

### Sample Data
The repository includes sample data for testing:

- **15 categories** (sneakers, sandals, boots, etc.)
- **105 verticals** (brand-specific categories)
- **440 trends** (fashion trend data)
- **248 images** (trend reference images)
- **Sample products** (CSV format for testing)

## 🔧 Development

### Available Commands
```bash
# Docker operations
docker-compose up -d          # Start all services
docker-compose down           # Stop all services
docker-compose logs api       # View API logs

# Database operations
cd scripts
./setup_database.sh          # Initialize database
./run_import.sh              # Import sample data

# Frontend development
cd frontend
npm run dev                  # Development server
npm run build               # Production build

# Backend development
cd api
uvicorn app.main:app --reload  # Development server
```

## 🧪 Testing

### Sample Data Testing
```bash
# Test CSV upload
cd scripts
python upload_csv_test.py

# Test API endpoints
curl http://localhost:8001/api/v1/products?limit=5
curl http://localhost:8001/api/v1/categories
```

## 📊 Monitoring & Health

### Health Checks
```bash
# API health
curl http://localhost:8001/health

# Database status
curl http://localhost:8001/api/v1/stats
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Made with ❤️ for the fashion industry**