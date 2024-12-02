import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import dotenv
from models.model import Base  # Import Base from models.py
# Load environment variables
dotenv.load_dotenv()

# Database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./energy_saving_app.db"
#engine = create_engine('postgresql://localhost/[energy_saving_app.db]')
#SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")
# Create the SQLAlchemy engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Initialize the sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Drop existing tables and recreate them
#Base.metadata.drop_all(bind=engine)  # This will drop the tables
#Base.metadata.create_all(bind=engine)  # This will recreate the tables

# Dependency function for session management (optional, useful for web apps)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
