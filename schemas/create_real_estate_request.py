# pydantic_validation.py

from pydantic import BaseModel, Field
from typing import Optional

class CreateRealEstateRequest(BaseModel):
    square_area: int = Field(..., gt=0)
    real_estate_type: str
    year_built: int = Field(..., gt=1800)
    insulation_quality: str
    energy_source: Optional[str] = None
    location: Optional[str] = None

class EmailTipsRequest(BaseModel):
    recipient: str
    subject: Optional[str] = "Energy-Saving Tips"
