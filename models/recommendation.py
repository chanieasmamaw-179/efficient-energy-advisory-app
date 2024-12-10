"""
represents recommendation tables in the database and store the recommendation messages
"""

# Standard library imports
from datetime import datetime  # Provides date and time functions

# Third-party imports
# SQLAlchemy data types and functions
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
# SQLAlchemy ORM capabilities for defining relationships
from sqlalchemy.orm import relationship

# Local imports
from .base import Base  # Import shared Base class from the local module


class Recommendation(Base):
    """
     Represents the Recommendation table in the database.
    """
    __tablename__ = 'recommendations'

    id = Column(Integer, primary_key=True)
    category = Column(String(50), nullable=False, default="General")
    message = Column(String, index=True)
    estimated_savings = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    real_estate_id = Column(Integer, ForeignKey('real_estates.id'), nullable=False)

    user = relationship("User", back_populates="recommendations")
    real_estate = relationship("RealEstate", back_populates="recommendations")
