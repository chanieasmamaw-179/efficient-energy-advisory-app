import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import dotenv
from models.base import Base  # Import Base from model.py

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

# Dependency function for session management (useful for FastAPI)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
