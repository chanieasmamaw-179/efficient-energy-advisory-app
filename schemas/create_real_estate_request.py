"""
This module contains Pydantic models and field definitions for handling
data validation and serialization in the application.
"""

from pydantic import BaseModel, Field
from typing import Optional

class CreateRealEstateRequest(BaseModel):
    """
    This module defines Pydantic models for validating and serializing data related to
real estate creation and email tip requests.
    """
    square_area: int = Field(..., gt=0)
    real_estate_type: str
    year_built: int = Field(..., gt=1800)
    insulation_quality: str
    energy_source: Optional[str] = None
    location: Optional[str] = None

class EmailTipsRequest(BaseModel):
    """
     Schema for sending energy-saving tips via email.
    """
    recipient: str
    subject: Optional[str] = "Energy-Saving Tips"
