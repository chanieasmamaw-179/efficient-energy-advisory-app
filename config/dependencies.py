from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.database import SessionLocal
import logging



logger = logging.getLogger(__name__)

def db_dependency():
    db = SessionLocal()
    try:
        yield db  # Yield the session to the endpoint
    except Exception as e:  # Catch only Exception or its subclasses
        db.rollback()  # Roll back any pending transaction in case of an error
        logger.error(f"Error connecting to the database_db: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error",
        )  # Re-raise as HTTPException to alert FastAPI
    finally:
        db.close()  # Ensure the config session is always closed
