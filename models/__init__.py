from .base import Base
from .user import User
from models.real_estates import RealEstate
from models.recomendation import Recommendation
from .notification import Notification
from .weather_recommendation import WeatherBasedRecommendation

# Add models to a list for easier use with tools like Alembic
__all__ = [
    "Base",
    "User",
    "RealEstate",
    "Recommendation",
    "Notification",
    "WeatherBasedRecommendation",
]
