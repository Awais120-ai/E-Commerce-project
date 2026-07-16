from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.crud import get_user_by_email, create_user
from app.utils.password import verify_password
from app.utils.jwt import create_access_token
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_user(db, user)

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    db_user = get_user_by_email(db, form_data.username)
    print("LOGIN EMAIL:", form_data.username)
    print("USER:", db_user)
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
        print("PASSWORD FROM FRONTEND:", form_data.password)
        print("PASSWORD FROM DB:", db_user.password)


    if not verify_password(form_data.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token({"sub": str(db_user.id)})
    return {"access_token": token, "token_type": "bearer"}