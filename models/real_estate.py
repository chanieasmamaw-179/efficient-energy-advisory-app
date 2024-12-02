# real_estate.py
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models.model import RealEstate
from pydantic import BaseModel, Field
from typing import Optional

class CreateRealEstateRequest(BaseModel):
    square_area: int = Field(..., gt=0)
    real_estate_type: str
    year_built: int = Field(..., gt=1800)
    insulation_quality: str
    energy_source: Optional[str] = None
    location: Optional[str] = None

async def register_property(create_real_estate_request: CreateRealEstateRequest, db: Session, user_id: int):
    """
    Registers a new real estate property for the user.
    """
    try:
        new_real_estate = RealEstate(
            square_area=create_real_estate_request.square_area,
            real_estate_type=create_real_estate_request.real_estate_type,
            year_built=create_real_estate_request.year_built,
            insulation_quality=create_real_estate_request.insulation_quality,
            energy_source=create_real_estate_request.energy_source,
            location=create_real_estate_request.location,
            user_id=user_id
        )
        db.add(new_real_estate)
        db.commit()
        db.refresh(new_real_estate)
        return new_real_estate
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating property.")
