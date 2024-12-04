# Import the correct Base class from models.base
from models.base import Base

# Use the existing Base from your project
target_metadata = Base.metadata

# Define the model class inheriting from the imported Base
class Model(Base):  # Capitalize class names by convention

    # Configuration for SQLAlchemy (optional)
    class Config:
        from_attributes = False
