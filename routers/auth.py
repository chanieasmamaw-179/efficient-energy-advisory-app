"""
This module implements user authentication and management functionality,
including login, token generation, password hashing, and user schemas.
"""

# Standard Library Imports
import os
import logging
import re
from datetime import datetime, timedelta
from typing import Optional

# Third-Party Imports
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, validator
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from passlib.context import CryptContext
from jwt import encode

# Local Imports
from models.model import User  # Assuming this is your ORM model for the User entity
from config.dependencies import db_dependency  # Dependency for database session

# Setting up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter(prefix="/auth", tags=["auth"])

# Load environment variables
SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "180"))

# Security settings
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/token")


class UserCreateRequest(BaseModel):
    """Schema for creating a new user."""
    full_name: str
    email: EmailStr
    phone_number: str
    password: str
    confirm_password: str

    @validator("password")
    def validate_password(cls, password: str) -> str:
        if len(password) < 8 or not re.search(r'\d', password) or not re.search(r'[A-Z]', password) or not re.search(r'[a-z]', password):
            raise ValueError("Password must be at least 8 characters long and include uppercase, lowercase, and a digit.")
        return password

    @validator("confirm_password")
    def validate_confirm_password(cls, confirm_password: str, values: dict) -> str:
        if "password" in values and confirm_password != values["password"]:
            raise ValueError("Passwords do not match.")
        return confirm_password

    @validator("phone_number")
    def validate_phone_number(cls, phone_number: str) -> str:
        if not re.match(r"^\+?\d{10,15}$", phone_number):
            raise ValueError("Invalid phone number format. Example: +1234567890")
        return phone_number


class Token(BaseModel):
    access_token: Optional[str] = None
    token_type: str = "bearer"


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreateRequest, db: Session = Depends(db_dependency)):
    """Register a new user."""
    try:
        existing_user = db.query(User).filter(
            (User.email == user.email) | (User.phone_number == user.phone_number)).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email or phone number already registered.")

        hashed_password = bcrypt_context.hash(user.password)
        new_user = User(name=user.full_name, email=user.email, phone_number=user.phone_number,
                        hash_password=hashed_password)

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {"message": "User successfully registered", "id": new_user.id}
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error occurred.")
    finally:
        db.close()


@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(db_dependency)):
    """Authenticate a user and issue a JWT token."""
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not bcrypt_context.verify(form_data.password, user.hash_password):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    access_token = create_access_token({"sub": user.email})
    return Token(access_token=access_token)


def get_current_user(token: str = Depends(oauth2_bearer), db: Session = Depends(db_dependency)):
    """Retrieve the currently logged-in user."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user = db.query(User).filter(User.email == payload.get("sub")).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token.")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token.")
