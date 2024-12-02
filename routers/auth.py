"""
This module implements user authentication and management functionality
including login, token generation, password hashing, and user schemas.

Dependencies:
- Database interaction is handled via SQLAlchemy.
- JWT for token generation.
- FastAPI for API routing and dependency injection.
- Twilio for sending SMS notifications.
"""
# Standard Library Imports
import os
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

# Third-Party Imports
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, validator, EmailStr
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from passlib.context import CryptContext
import jwt
from jwt import PyJWTError
from jwt.exceptions import PyJWTError

# Local Imports
from models.model import User  # Assuming this is your ORM model for the User entity
from  config.dependencies import  db_dependency # Dependency for config session


# Setting up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter(prefix="/user_registration", tags=["user_registration"])

# Load SECRET_KEY from environment variable
SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv(
    "ACCESS_TOKEN_EXPIRE_MINUTES", "180"))


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/user_registration/token")


class UserCreateRequest(BaseModel):
    """
       Schema for creating a new user.

       Attributes:
           email (EmailStr): The user's email address, which must be a valid email format.
           password (str): The user's password. It should be strong and secure.
           full_name (Optional[str]): The user's full name, which is optional.
       """
    full_name: str
    password: str
    confirm_password: str
    email: EmailStr
    phone_number: str

    @dataclass
    class Config:
        """
        Configuration class for the Pydantic model.

        Attributes:
            from_attributes (bool): Enables creating a model instance from
            object attributes. When set to True, Pydantic will attempt to populate
            model fields directly from the attributes of an object.
        """
        from_attributes = True

    @validator("phone_number")
    def validate_phone_number(cls, phone_number: str) -> str:
        """
            Validates the format of the phone number.

            The phone number must:
            - Optionally start with a "+" (e.g., for international numbers).
            - Contain only digits, with a length between 10 and 15 characters.
        """

        # Adjust this regex based on your desired phone number format
        if not re.match(r"^\+?\d{10,15}$", phone_number):
            raise ValueError("Phone number must be a valid format (e.g., +1234567890).")
        return phone_number

    @validator("password")
    def password_complexity(cls, password: str) -> str:
        """
            Validates the complexity of the password.
            The password must meet the following requirements:
            - Be at least 8 characters long.
            - Contain at least one digit.
            - Contain at least one uppercase letter.
            - Contain at least one lowercase letter.
        """
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not re.search(r"\d", password):  # Check for a digit
            raise ValueError("Password must contain at least one digit.")
        if not re.search(r"[A-Z]", password):  # Check for an uppercase letter
            raise ValueError("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", password):  # Check for a lowercase letter
            raise ValueError("Password must contain at least one lowercase letter.")
        return password

    @validator("confirm_password")
    def passwords_match(cls, confirm_password, values):
        """
       Validates that the password and confirm_password fields match and are not empty.
       This method is used to ensure that the password and its confirmation match.
        It also checks that neither the password nor the confirm_password is empty.
        """
        password = values.get("password")
        if password and confirm_password != password:
            raise ValueError("Passwords do not match.")
        elif not password or not confirm_password:
            raise ValueError("Password and confirm_password cannot be empty.")
        return confirm_password


class Token(BaseModel):
    """
    Token model used for returning authentication tokens in the response.
    """
    access_token: Optional[str] = None
    token_type: Optional[str] = None
    error: Optional[str] = None
    detail: Optional[str] = None


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Creates an access token (JWT) for a user with the provided data.
    This function generates a JWT token that contains the provided data and sets an expiration
    time for the token. The expiration time defaults to a pre-configured value but can be
    customized by passing an `expires_delta` value.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})

    try:
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    except jwt.PyJWTError as e:
        logger.error(f"JWT encoding failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="JWT encoding failed.")

@router.post("/", status_code=status.HTTP_201_CREATED, operation_id="user_registration_create")
async def user_registration(create_user_request: UserCreateRequest, db: Session = Depends(db_dependency)):
    """
     Registers a new user in the system.
        This function handles the registration process for a new user. It validates the user's
        information, checks if the provided email already exists in the system, and if not,
        creates a new user record in the config. The password is hashed before storing it
        securely in the config.
    """
    try:
        # Check if email already exists
        existing_user_by_email = db.query(User).filter(User.email == create_user_request.email).first()
        if existing_user_by_email:
            logger.warning(f"Registration attempt failed: Email {create_user_request.email} already registered.")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered.")

        # Check if phone number already exists
        existing_user_by_phone = db.query(User).filter(User.phone_number == create_user_request.phone_number).first()
        if existing_user_by_phone:
            logger.warning(f"Registration attempt failed: Phone number {create_user_request.phone_number} already registered.")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone number already registered.")

        # Hash the password and create the new user
        hashed_password = bcrypt_context.hash(create_user_request.password)
        new_user = User(
            name=create_user_request.full_name,
            email=create_user_request.email,
            hash_password=hashed_password,
            phone_number=create_user_request.phone_number,
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {"message": "User created successfully", "id": new_user.id}

    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error.")

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected error.")


@router.post("/token", response_model=Token, operation_id="login_create_token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(db_dependency)):
    """
     Handles user login and generates an access token.
     Verifies the user's credentials (email and password) and generates a JWT access token if successful.
    """
    try:
        # Try to fetch the user from the config by email
        user = db.query(User).filter(User.email == form_data.username).first()

        # Check if the user exists
        if not user:
            error_message = f"Login attempt failed: User with email {form_data.username} not found."
            logger.warning(error_message)
            return Token(
                error="Authentication Failed",
                detail="Incorrect email or password",
            )

        # Verify the password matches
        if not bcrypt_context.verify(form_data.password, user.hash_password):
            error_message = f"Login attempt failed: Incorrect password for user with email {form_data.username}."
            logger.warning(error_message)
            return Token(
                error="Authentication Failed",
                detail="Incorrect email or password",
            )

        # If authentication is successful, create an access token
        access_token = create_access_token(data={"sub": user.email})
        return Token(
            access_token=access_token,
            token_type="bearer",
        )

    except SQLAlchemyError as e:
        logger.error(f"Database query failed during login: {str(e)}")
        return Token(
            error="Database Error",
            detail="Database query failed.",
        )

    except Exception as e:
        logger.error(f"An unexpected error occurred during login: {str(e)}")
        return Token(
            error="Unexpected Error",
            detail="Unexpected error during login.",
        )


@router.post("/token", response_model=Token, operation_id="login_post")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(db_dependency)):
    """
         Handles user login and generates an access token.
     Verifies the user's credentials (email and password) and generates a JWT access token if successful.
    """
    try:
        # Try to fetch the user from the config by email
        user = db.query(User).filter(User.email == form_data.username).first()

        # Check if the user exists
        if not user:
            error_message = f"Login attempt failed: User with email {form_data.username} not found."
            logger.warning(error_message)
            return Token(
                error="Authentication Failed",
                detail="Incorrect email or password",
            )

        # Verify the password matches
        if not bcrypt_context.verify(form_data.password, user.hash_password):
            error_message = f"Login attempt failed: Incorrect password for user with email {form_data.username}."
            logger.warning(error_message)
            return Token(
                error="Authentication Failed",
                detail="Incorrect email or password",
            )

        # If authentication is successful, create an access token
        access_token = create_access_token(data={"sub": user.email})
        return Token(
            access_token=access_token,
            token_type="bearer",
        )

    except SQLAlchemyError as e:
        logger.error(f"Database query failed during login: {str(e)}")
        return Token(
            error="Database Error",
            detail="Database query failed.",
        )

    except Exception as e:
        logger.error(f"An unexpected error occurred during login: {str(e)}")
        return Token(
            error="Unexpected Error",
            detail="Unexpected error during login.",
        )
def get_current_user(token: str = Depends(oauth2_bearer), db: Session = Depends(db_dependency)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email: str = payload.get("sub")

        if user_email is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials.")

        user = db.query(User).filter(User.email == user_email).first()

        if user is None:
            raise HTTPException(status_code=401, detail="User not found.")

        return user
    except jwt.ExpiredSignatureError:
        logger.error("Token expired")
        raise HTTPException(status_code=401, detail="Token has expired.")
    except jwt.JWTError as e:
        logger.error(f"JWT Error: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid token.")

"""
def get_current_user(db: Session = Depends(db_dependency)):
    # Assuming there's a method to get the current authenticated user
    user = db.query(User).filter(User.id == 1).first()  # Or use your logic to fetch the user
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
"""