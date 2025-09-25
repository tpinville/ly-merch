# MyApp Monorepo

Full-stack monorepo:
- **frontend**: React + Vite, built and served via **Nginx**
- **api**: FastAPI (Python 3.11), SQLAlchemy
- **db**: MySQL 8 with healthcheck
- **orchestration**: Docker Compose
- **extras**: Adminer at http://localhost:8081 for quick DB access

## Quick Start

1. Adjust secrets in `.env` if needed.
2. Build & run:
   ```bash
   make up
