# app/routers/mechanics.py

from fastapi import APIRouter, Depends, HTTPException
from typing import List
from pydantic import BaseModel
import asyncpg

router = APIRouter(prefix="/mechanics", tags=["Mechanics"])

# ────────────────────────────── SCHEMAS ──────────────────────────────

class MechanicBase(BaseModel):
    phone: str
    name: str
    location: str | None = None
    is_verified: bool = False
    rating: int = 0
    jobs_completed: int = 0


class MechanicCreate(MechanicBase):
    pass


class MechanicUpdate(BaseModel):
    phone: str | None = None
    name: str | None = None
    location: str | None = None
    is_verified: bool | None = None
    rating: int | None = None
    jobs_completed: int | None = None


class Mechanic(MechanicBase):
    id: int

    class Config:
        from_attributes = True  # For Pydantic v2 compatibility


# ────────────────────────────── DEPENDENCY ──────────────────────────────

async def get_db() -> asyncpg.Connection:
    from ..main import pool  # Import pool from main.py
    async with pool.acquire() as conn:
        yield conn


# ────────────────────────────── ENDPOINTS ──────────────────────────────

@router.post("/", response_model=Mechanic)
async def create(mechanic: MechanicCreate, db: asyncpg.Connection = Depends(get_db)):
    query = """
        INSERT INTO mechanics (phone, name, location, is_verified, rating, jobs_completed)
        VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING id, phone, name, location, is_verified, rating, jobs_completed
    """
    result = await db.fetchrow(
        query,
        mechanic.phone,
        mechanic.name,
        mechanic.location,
        mechanic.is_verified,
        mechanic.rating,
        mechanic.jobs_completed
    )
    if not result:
        raise HTTPException(status_code=500, detail="Failed to create mechanic")
    return dict(result)


@router.get("/", response_model=List[Mechanic])
async def read_all(db: asyncpg.Connection = Depends(get_db)):
    query = """
        SELECT id, phone, name, location, is_verified, rating, jobs_completed
        FROM mechanics
        ORDER BY id DESC
    """
    rows = await db.fetch(query)
    return [dict(r) for r in rows]


@router.get("/{mechanic_id}", response_model=Mechanic)
async def read_one(mechanic_id: int, db: asyncpg.Connection = Depends(get_db)):
    query = """
        SELECT id, phone, name, location, is_verified, rating, jobs_completed
        FROM mechanics
        WHERE id = $1
    """
    result = await db.fetchrow(query, mechanic_id)
    if not result:
        raise HTTPException(status_code=404, detail="Mechanic not found")
    return dict(result)


@router.patch("/{mechanic_id}", response_model=Mechanic)
async def update(
    mechanic_id: int,
    update: MechanicUpdate,
    db: asyncpg.Connection = Depends(get_db)
):
    data = update.dict(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=400, detail="No fields to update")

    set_parts = []
    values = []
    for idx, (key, value) in enumerate(data.items(), start=1):
        set_parts.append(f"{key} = ${idx}")
        values.append(value)

    values.append(mechanic_id)
    query = f"""
        UPDATE mechanics
        SET {', '.join(set_parts)}
        WHERE id = ${len(values)}
        RETURNING id, phone, name, location, is_verified, rating, jobs_completed
    """
    result = await db.fetchrow(query, *values)
    if not result:
        raise HTTPException(status_code=404, detail="Mechanic not found")
    return dict(result)


@router.delete("/{mechanic_id}")
async def delete(mechanic_id: int, db: asyncpg.Connection = Depends(get_db)):
    query = "DELETE FROM mechanics WHERE id = $1 RETURNING id"
    result = await db.fetchrow(query, mechanic_id)
    if not result:
        raise HTTPException(status_code=404, detail="Mechanic not found")
    return {"detail": "Mechanic deleted successfully"}