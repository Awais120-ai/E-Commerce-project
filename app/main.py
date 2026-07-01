from fastapi import FastAPI

from app.database import Base, engine
import app.models
from fastapi.staticfiles import StaticFiles
from app.routers import auth, users, products, categories, cart, orders, wishlist
from app.routers import payments

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="E-Commerce API",
    version="1.0.0"
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(products.router)
app.include_router(categories.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(wishlist.router)
app.include_router(payments.router)

@app.get("/")
def home():
    return {"message": "Welcome to E-Commerce API"}


@app.get("/health")
def health():
    return {"status": "Server Running"}

app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads"
)
