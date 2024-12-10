
"""
User model is created and user details is registered.
"""

# Standard library imports
# Import Enum from the standard library and alias it as PyEnum
from enum import Enum as PyEnum

# Third-party imports
# SQLAlchemy data types and functions
from sqlalchemy import Column, Integer, String, Enum, Boolean
# SQLAlchemy ORM capabilities for defining relationships
from sqlalchemy.orm import relationship

# Local imports
# Import shared Base class from the local module
from .base import Base



class NotificationFrequency(str, PyEnum):
    """
     Represents the User table in the database.
    """
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    SEASONALLY = "SEASONALLY"

class User(Base):
    """
    Represents a user in the system.
    This class maps to the 'users' table in the database and contains
    information such as the user's ID, username, email, and other details.
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    hash_password = Column(String, nullable=False)
    notification_frequency = Column(Enum(NotificationFrequency),
                                    default=NotificationFrequency.DAILY)
    preferred_weather_tips = Column(Boolean, default=True)
    phone_number = Column(String(50), nullable=False)

    # Relationships
    real_estates = relationship("RealEstate", back_populates="user",
                                cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="user",
                                   cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user",
                                 cascade="all, delete-orphan")
    weather_based_recommendations = relationship(
        "WeatherBasedRecommendation", back_populates="user", cascade="all, delete-orphan"
    )
