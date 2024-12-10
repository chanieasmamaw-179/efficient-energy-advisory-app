"""
Main module to set up and manage the database connection and ORM session using SQLAlchemy.
"""
# Standard library imports
from datetime import datetime, timedelta
import os
# Third-party imports
import dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# Local application imports
from models.base import Base
from models.notification import Notification
from models.recommendation import Recommendation

# Load environment variables
dotenv.load_dotenv()

# Retrieve database URL from environment variables
SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")
if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("Database URL not set in environment variables.")

# Create the SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Initialize the sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def clean_up_old_records():
    """
     Cleans up old records from the database.
    This function performs the following cleanup tasks:
    1. Deletes notifications older than 30 days from the Notification table.
    2. Deletes recommendations with expired conditions older than 30 days
       from the Recommendation table.
    """
    with SessionLocal() as session:
        # Example: Delete notifications older than 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        session.query(Notification).filter(Notification.timestamp < thirty_days_ago).delete()

        # Example: Delete recommendations with expired conditions
        session.query(Recommendation).filter(Recommendation.timestamp < thirty_days_ago).delete()

        session.commit()

# Dependency function for session management (useful for FastAPI)
def get_db():
    """
        Provides a database session for dependency injection.
    This function creates and yields a database session using SQLAlchemy's
    SessionLocal. It ensures that the session is properly closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
