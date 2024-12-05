import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import dotenv
from models.base import Base  # Import Base from model.py
from datetime import datetime, timedelta




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
    with SessionLocal() as session:
        # Example: Delete notifications older than 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        session.query(Notification).filter(Notification.timestamp < thirty_days_ago).delete()

        # Example: Delete recommendations with expired conditions
        session.query(Recommendation).filter(Recommendation.timestamp < thirty_days_ago).delete()

        session.commit()

# Dependency function for session management (useful for FastAPI)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
