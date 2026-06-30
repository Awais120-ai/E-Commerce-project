from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import Base, engine, SessionLocal
import app.models
import app.crud as crud
from app.schemas import UserCreate, UserResponse, UserUpdate

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="E-Commerce API",
    version="1.0.0"
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home():
    return {"message": "Welcome to E-Commerce API"}


@app.get("/health")
def health():
    return {"status": "Server Running"}


@app.post("/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db, user)


@app.get("/users", response_model=list[UserResponse])
def read_users(db: Session = Depends(get_db)):
    return crud.get_users(db)


@app.get("/users/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):

    updated = crud.update_user(db, user_id, user)

    if not updated:
        raise HTTPException(status_code=404, detail="User not found")

    return updated


@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):

    deleted = crud.delete_user(db, user_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "message": "User deleted successfully"
    }