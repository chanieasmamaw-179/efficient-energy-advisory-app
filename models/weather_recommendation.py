from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base  # Import shared Base

class WeatherBasedRecommendation(Base):
    """
    Represents weather-based recommendations for a user in the database.
    """
    __tablename__ = 'weather_based_recommendations'

    id = Column(Integer, primary_key=True)
    message = Column(String(500), nullable=False)
    temperature_condition = Column(String(100), nullable=False)
    weather_tips = Column(String(5000), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship("User", back_populates="weather_based_recommendations")
