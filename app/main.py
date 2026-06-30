from fastapi import FastAPI

from app.database import Base, engine
import app.models
from app.routers import auth, users

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="E-Commerce API",
    version="1.0.0"
)

app.include_router(auth.router)
app.include_router(users.router)


@app.get("/")
def home():
    return {"message": "Welcome to E-Commerce API"}


@app.get("/health")
def health():
    return {"status": "Server Running"}
