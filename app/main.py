from typing import List
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas
from .database import database, engine, SessionLocal

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.post("/users/", response_model=schemas.User)
async def create_user(user: schemas.UserCreate):
    query = models.User.__table__.insert().values(name=user.name, email=user.email)
    last_record_id = await database.execute(query)
    return {**user.dict(), "id": last_record_id}

@app.get("/users/{user_id}", response_model=schemas.User)
async def read_user(user_id: int):
    query = models.User.__table__.select().where(models.User.id == user_id)
    user = await database.fetch_one(query)
    if user is None:
        raise HTTPException(status_code=404, detail="User  not found")
    return user


@app.get("/users/", response_model=List[schemas.User])
async def read_users():
    query = models.User.__table__.select()
    users = await database.fetch_all(query)
    if not users:
        raise HTTPException(status_code=404, detail="No users found")
    return users