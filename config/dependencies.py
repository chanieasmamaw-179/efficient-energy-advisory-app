"""
This module provides the database session dependency for FastAPI endpoints.
Modules imported:
- FastAPI dependencies (Depends, HTTPException, status) for request handling.
- SQLAlchemy ORM for managing database interactions.
- Logging configuration for debugging and tracking.
"""

# Third-party imports
import logging
from fastapi import  HTTPException, status
#from sqlalchemy.orm import Session

# Local imports
from config.database import SessionLocal


logger = logging.getLogger(__name__)

def db_dependency():
    """
     Yields a database session, handles errors with rollback, and ensures closure.
    Raises a 500 HTTPException if an error occurs.
    """
    db = SessionLocal()
    try:
        yield db  # Yield the session to the endpoint
    except Exception as e:  # Catch only Exception or its subclasses
        db.rollback()  # Roll back any pending transaction in case of an error
        logger.error("Error connecting to the database_db %s:", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error",
        )  # Re-raise as HTTPException to alert FastAPI
    finally:
        db.close()  # Ensure the config session is always closed
