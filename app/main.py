from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine, SessionLocal
import app.models
from fastapi.staticfiles import StaticFiles
from app.routers import auth, users, products, categories, cart, orders, wishlist
from app.routers import payments
# Schemas for creating a default user
from app.schemas.user import UserCreate
import app.crud as crud
from app.routers import address

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="E-Commerce API",
    version="1.0.0"
)

# Allow CORS for all origins (development)
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Create a default admin user on startup (useful for quick testing)
# ---------------------------------------------------------------------------
@app.on_event("startup")
async def create_default_user():
    db = SessionLocal()
    try:
        default_email = "admin@example.com"
        # If the default user does not exist, create it
        if not crud.get_user_by_email(db, default_email):
            default_user = UserCreate(
                full_name="Admin User",
                email=default_email,
                password="admin123",
            )
            crud.create_user(db, default_user)
    finally:
        db.close()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(products.router)
app.include_router(categories.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(wishlist.router)
app.include_router(payments.router)
app.include_router(address.router)



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
