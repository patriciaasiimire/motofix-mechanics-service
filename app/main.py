from fastapi import FastAPI
from app.database import engine, Base
from app.routers import mechanics

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MOTOFIX Mechanics API",
    openapi_url="/openapi.json",
    docs_url="/docs"
)

app.include_router(mechanics.router)