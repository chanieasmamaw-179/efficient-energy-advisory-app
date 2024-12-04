from sqlalchemy import Column, Integer, String, Enum, Boolean
from sqlalchemy.orm import relationship
from .base import Base  # Import shared Base
from enum import Enum as PyEnum

class NotificationFrequency(str, PyEnum):
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    SEASONALLY = "SEASONALLY"

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    hash_password = Column(String, nullable=False)
    notification_frequency = Column(Enum(NotificationFrequency), default=NotificationFrequency.DAILY)
    preferred_weather_tips = Column(Boolean, default=True)
    phone_number = Column(String(50), nullable=False)

    # Relationships
    real_estates = relationship("RealEstate", back_populates="user", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    weather_based_recommendations = relationship(
        "WeatherBasedRecommendation", back_populates="user", cascade="all, delete-orphan"
    )
