from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas, database

router = APIRouter(prefix="/mechanics", tags=["Mechanics"])


@router.post("/", response_model=schemas.Mechanic)
def create(mechanic: schemas.MechanicCreate, db: Session = Depends(database.get_db)):
    db_m = models.Mechanic(**mechanic.dict())
    db.add(db_m)
    db.commit()
    db.refresh(db_m)
    return db_m


@router.get("/", response_model=List[schemas.Mechanic])
def read_all(db: Session = Depends(database.get_db)):
    return db.query(models.Mechanic).all()


@router.get("/{mechanic_id}", response_model=schemas.Mechanic)
def read_one(mechanic_id: int, db: Session = Depends(database.get_db)):
    m = db.query(models.Mechanic).filter(models.Mechanic.id == mechanic_id).first()
    if not m:
        raise HTTPException(404, "Mechanic not found")
    return m


@router.patch("/{mechanic_id}", response_model=schemas.Mechanic)
def update(mechanic_id: int, update: schemas.MechanicUpdate, db: Session = Depends(database.get_db)):
    m = db.query(models.Mechanic).filter(models.Mechanic.id == mechanic_id).first()
    if not m:
        raise HTTPException(404, "Mechanic not found")

    data = update.dict(exclude_unset=True)
    for key, value in data.items():
        setattr(m, key, value)

    db.commit()
    db.refresh(m)
    return m


@router.delete("/{mechanic_id}", response_model=schemas.Mechanic)
def delete(mechanic_id: int, db: Session = Depends(database.get_db)):
    m = db.query(models.Mechanic).filter(models.Mechanic.id == mechanic_id).first()
    if not m:
        raise HTTPException(404, "Mechanic not found")
    db.delete(m)
    db.commit()
    return m