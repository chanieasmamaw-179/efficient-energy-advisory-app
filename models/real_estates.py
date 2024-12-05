from fastapi import HTTPException
from sqlalchemy.orm import relationship, Session
from starlette import status
from models import Base
from schemas.create_real_estate_request import CreateRealEstateRequest
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship


class RealEstate(Base):
    """
        Registers a new real estate property for the user.
        Args:
            create_real_estate_request (CreateRealEstateRequest): Data for the new property to register.
        Returns:
            RealEstate: The created real estate object with its database entry.
        Raises:
            HTTPException: If there is an error creating the property.
        """

    __tablename__ = 'real_estates'

    id = Column(Integer, primary_key=True)
    square_area = Column(Integer, nullable=False)
    real_estate_type = Column(String(50), nullable=False)
    year_built = Column(Integer, nullable=False)
    insulation_quality = Column(String(50), nullable=False)
    energy_source = Column(String(50), nullable=True)
    location = Column(String(100), nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="real_estates")

    recommendations = relationship("Recommendation", back_populates="real_estate", cascade="all, delete-orphan")


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
