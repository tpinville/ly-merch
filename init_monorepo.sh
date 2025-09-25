#!/usr/bin/env bash

set -euo pipefail

APP_NAME="${1:-myapp}"
APP_DIR="${APP_NAME}"

echo "Scaffolding monorepo in: ${APP_DIR}"
mkdir -p "$APP_DIR"
cd "$APP_DIR"

########################
# Root: git + ignores  #
########################
git init -q
cat > .gitignore <<'__EOF__'
# Node / frontend
node_modules/
dist/
.vite/
*.log

# Python
__pycache__/
*.pyc
.venv/

# Docker
.env
*.env.local
volume_data/

# IDE
.vscode/
.idea/
.DS_Store
__EOF__

########################
# .env (root)          #
########################
cat > .env <<'__EOF__'
# ---- Global ----
PROJECT_NAME=myapp

# ---- MySQL ----
MYSQL_ROOT_PASSWORD=changeme_root
MYSQL_DATABASE=myapp
MYSQL_USER=myapp
MYSQL_PASSWORD=changeme_user

# ---- Ports ----
API_PORT=8000
FRONTEND_PORT=8080

# ---- API ----
API_LOG_LEVEL=info
CORS_ORIGINS=http://localhost:8080,http://127.0.0.1:8080
DB_URL=mysql+pymysql://myapp:changeme_user@db:3306/myapp
__EOF__

########################
# Docker Compose       #
########################
mkdir -p infra
cat > docker-compose.yml <<'__EOF__'
services:
  db:
    image: mysql:8.0
    container_name: ${PROJECT_NAME}_db
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: ${MYSQL_DATABASE}
      MYSQL_USER: ${MYSQL_USER}
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
    ports:
      - "3306:3306"
    volumes:
      - db_data:/var/lib/mysql
    healthcheck:
      test: ["CMD-SHELL", "mysqladmin ping -h localhost -u${MYSQL_USER} -p${MYSQL_PASSWORD} --silent"]
      interval: 5s
      timeout: 3s
      retries: 20

  api:
    build:
      context: ./api
      dockerfile: Dockerfile
    container_name: ${PROJECT_NAME}_api
    env_file: .env
    ports:
      - "${API_PORT}:8000"
    depends_on:
      db:
        condition: service_healthy

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: ${PROJECT_NAME}_frontend
    env_file: .env
    ports:
      - "${FRONTEND_PORT}:80"
    depends_on:
      - api

  adminer:
    image: adminer:4
    container_name: ${PROJECT_NAME}_adminer
    ports:
      - "8081:8080"
    depends_on:
      - db

volumes:
  db_data:
__EOF__

########################
# Makefile             #
########################
cat > Makefile <<'__EOF__'
SHELL := /bin/bash

up:
\tdocker compose --env-file .env up -d --build

down:
\tdocker compose down

logs:
\tdocker compose logs -f

ps:
\tdocker compose ps

reset-db:
\tdocker compose down -v
\tdocker compose up -d db
\tdocker compose logs -f db

curl-api:
\tcurl -s http://localhost:8000/health | jq .

open-adminer:
\t@echo "Open http://localhost:8081 (Server: db, User: $$MYSQL_USER, Pass: $$MYSQL_PASSWORD, DB: $$MYSQL_DATABASE)"
__EOF__

########################
# API (FastAPI)        #
########################
mkdir -p api/app
cat > api/requirements.txt <<'__EOF__'
fastapi
uvicorn[standard]
sqlalchemy>=2.0
pymysql
python-dotenv
__EOF__

cat > api/Dockerfile <<'__EOF__'
# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY app /app/app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
__EOF__

cat > api/app/main.py <<'__EOF__'
import os
from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text, create_engine

API_LOG_LEVEL = os.getenv("API_LOG_LEVEL", "info")
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]
DB_URL = os.getenv("DB_URL", "mysql+pymysql://myapp:changeme_user@db:3306/myapp")

engine = create_engine(DB_URL, pool_pre_ping=True, future=True)

app = FastAPI(title="MyApp API", version="0.1.0")

if CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.get("/health")
def health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_ok = True
    except Exception as e:
        db_ok = False
    return {"status": "ok", "db": db_ok}

@app.get("/items")
def list_items() -> List[dict]:
    # Demo endpoint — replace with real models/tables
    return [{"id": 1, "name": "Hello"}, {"id": 2, "name": "World"}]
__EOF__

########################
# Frontend (Vite+React)#
########################
mkdir -p frontend/{public,src}
cat > frontend/package.json <<'__EOF__'
{
  "name": "frontend",
  "private": true,
  "version": "0.0.1",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview --port 4173"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.1",
    "vite": "^5.4.0"
  }
}
__EOF__

cat > frontend/index.html <<'__EOF__'
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <title>MyApp Frontend</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
__EOF__

cat > frontend/src/main.jsx <<'__EOF__'
import React from "react";
import { createRoot } from "react-dom/client";

const API_URL = (import.meta.env.VITE_API_BASE || "http://localhost:8000");

function App() {
  const [health, setHealth] = React.useState(null);

  React.useEffect(() => {
    fetch(`${API_URL}/health`)
      .then(r => r.json())
      .then(setHealth)
      .catch(() => setHealth({ status: "error" }));
  }, []);

  return (
    <main style={{ fontFamily: "system-ui", padding: 24 }}>
      <h1>MyApp Frontend (React + Vite)</h1>
      <p>API base: {API_URL}</p>
      <pre>{JSON.stringify(health, null, 2)}</pre>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
__EOF__

cat > frontend/vite.config.js <<'__EOF__'
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: true,
    host: true
  },
  preview: {
    port: 4173
  }
});
__EOF__

# Nginx to serve built assets
mkdir -p frontend/nginx
cat > frontend/nginx/default.conf <<'__EOF__'
server {
    listen 80;
    server_name _;

    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri /index.html;
    }
}
__EOF__

cat > frontend/Dockerfile <<'__EOF__'
# syntax=docker/dockerfile:1

# Build stage
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json /app/
RUN npm install
COPY . /app
RUN npm run build

# Runtime stage
FROM nginx:alpine
COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
__EOF__

########################
# Root README          #
########################
cat > README.md <<'__EOF__'
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
__EOF__
