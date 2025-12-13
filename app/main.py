# app/main.py

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncpg
from contextlib import asynccontextmanager
import logging

from app.routers import mechanics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ────────────────────────────── DATABASE POOL ──────────────────────────────
pool: asyncpg.Pool

@asynccontextmanager
async def lifespan(app: FastAPI):
    global pool
    dsn = os.getenv("DATABASE_URL")
    if not dsn:
        raise RuntimeError("DATABASE_URL environment variable is not set")
    pool = await asyncpg.create_pool(dsn=dsn)
    logger.info("Mechanics service: Database pool created successfully")
    yield
    await pool.close()
    logger.info("Mechanics service: Database pool closed")

app = FastAPI(
    title="MOTOFIX Mechanics API",
    version="1.0.0",
    description="CRUD API for managing mechanics (onboarding, verification, profile)",
    openapi_url="/openapi.json",
    docs_url="/docs",
    lifespan=lifespan
)

# ────────────────────────────── CORS ──────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://motofix-control-center.onrender.com",  # Admin dashboard / frontend
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ────────────────────────────── MAKE POOL AVAILABLE ──────────────────────────────
# Routers can access the pool via a dependency (we'll add it in mechanics.py if needed)

app.include_router(mechanics.router)