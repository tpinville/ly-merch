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
