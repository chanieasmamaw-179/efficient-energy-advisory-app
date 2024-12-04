from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base  # Import shared Base

class Recommendation(Base):
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
