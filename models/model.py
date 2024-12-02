"""
This module provides functionality related to recommendations,
including the creation and management of recommendations with
timestamps for tracking purposes.
"""
from datetime import datetime
from enum import Enum as PyEnum  # Enum for notification frequency,
                                 # An Enum is a set of symbolic names bound to unique values.

# Third-Party Imports
from dataclasses import dataclass
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


# Base class for all SQLAlchemy models, it's a factory function that constructs a base class.
Base = declarative_base()

class NotificationFrequency(str, PyEnum):
    """
    Enum class to define possible notification frequencies for users.

    This class represents the frequency with which notifications can be sent to users.
    It supports:
    - Daily
    - Weekly
    - Monthly
    - Seasonally
    """
    DAILY = "DAILY"   # Default is DAILY
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    SEASONALLY = "SEASONALLY"

@dataclass
class User(Base):
    """
    Define User table/model, which stores user account information.

    This model represents a user in the system, storing their account details such as
    name, email, password, notification frequency, preferred weather tips, and phone
    number. It also defines the relationships to other models such as RealEstate,
    Recommendation, Notification, and WeatherBasedRecommendation.
    """
    __tablename__ = 'users'

    def __init__(self, name, email, hash_password, phone_number=None):
        self.name = name
        self.email = email
        self.hash_password = hash_password
        self.phone_number = phone_number

    # Primary key for unique user identification
    id = Column(Integer, primary_key=True)  # Auto-incrementing primary key for users
    name = Column(String(100), nullable=False)  # User's full name (non-nullable)
    email = Column(String(150), unique=True, nullable=False)  # Unique email address (non-nullable)
    hash_password = Column(String, nullable=False)  # Hashed password (non-nullable)
    notification_frequency = Column(Enum(NotificationFrequency),
                                    default=NotificationFrequency.DAILY)  # Notification frequency
    preferred_weather_tips = Column(Boolean, default=True)
    # Flag indicating preference for weather tips
    phone_number = Column(String(50), nullable=False)  # User's phone number (non-nullable)

    # Relationships with other tables
    real_estates = relationship("RealEstate", back_populates="user",
                                cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="user",
                                   cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user",
                                 cascade="all, delete-orphan")
    weather_based_recommendations = relationship("WeatherBasedRecommendation",
                                                 back_populates="user",
                                                 cascade="all, delete-orphan")


class RealEstate(Base):
    """
    Define RealEstate table/model, which stores details about a user's real estate properties.

    This model represents a property owned by a user, including details such as square footage,
    type of property, year built, insulation quality, energy source, and location. It also defines
    the relationship with the User model.
    """
    __tablename__ = 'real_estates'

    # Primary key for unique property identification
    id = Column(Integer, primary_key=True)
    square_area = Column(Integer, nullable=False)  # Prt.'s size in square feet
    real_estate_type = Column(String(50), nullable=False)  # Type of prt. (e.g., residence, factory)
    year_built = Column(Integer, nullable=False)  # Year the prt was built
    insulation_quality = Column(String(50), nullable=False)  # Quality of insulation in the prt
    energy_source = Column(String(50), nullable=True)  # Energy source used by the prt (optional)
    location = Column(String(100), nullable=False)  # prt location

    # Foreign key to associate prt with a user
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="real_estates")

    # Relationship to the recommendations related to this prt
    recommendations = relationship("Recommendation", back_populates="real_estate",
                                   cascade="all, delete-orphan")
 # prt is the abbreviation of property

class Recommendation(Base):
    """
    Define Recommendation table/model, which stores recommendations for users based on
    their data.
    This model stores recommendations for users, such as suggestions for new insulation
     or maintenance.
    It includes information like the recommendation's category, message, estimated
    savings, and timestamp.
    """
    __tablename__ = 'recommendations'

    # Primary key for unique recommendation identification
    id = Column(Integer, primary_key=True)
    category = Column(String(50), nullable=False, default="General")  # estimated cost
    message = Column(String, index=True)
    estimated_savings = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)  # Timestamp of the recommendation

    # Foreign keys to associate recommendation with a user and real estate
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    real_estate_id = Column(Integer, ForeignKey('real_estates.id'), nullable=False)

    # Relationships to User and RealEstate models
    user = relationship("User", back_populates="recommendations")
    real_estate = relationship("RealEstate", back_populates="recommendations")


class Notification(Base):
    """
    Define Notification table/model, which stores notifications for users.

    This model stores notifications sent to users, including the notification's message,
    timestamp, status (e.g., SMS sent status), and the user it belongs to.
    """
    __tablename__ = 'notifications'

    # Primary key for unique notification identification
    id = Column(Integer, primary_key=True)
    message = Column(String(500), nullable=False, default="read")
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), nullable=False, default="SMS sent successfully", index=True)

    # Foreign key to associate notification with a user
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship("User", back_populates="notifications")


class WeatherBasedRecommendation(Base):
    """
    Define WeatherBasedRecommendation table/model, which stores recommendations based
    on weather conditions.

    This model stores weather-based recommendations, including the temperature condition and
    weather tips for the user.
    """
    __tablename__ = 'weather_based_recommendations'

    # Primary key for unique recommendation identification
    id = Column(Integer, primary_key=True)
    message = Column(String(500), nullable=False)  # Message for the weather-based recommendation
    temperature_condition = Column(String(100), nullable=False)
    weather_tips = Column(String(5000), nullable=False)  # Detailed weather tips
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Foreign key to associate recommendation with a user
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship("User", back_populates="weather_based_recommendations")
