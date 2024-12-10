# Standard library imports
import os
from asyncio import to_thread
from asyncio.log import logger
from typing import Dict, Optional

# Third-party imports
from fastapi import APIRouter, Depends, Query, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import FileResponse

# Local application imports
from config.dependencies import db_dependency
from models.energy_cost_estimation_engine import (
    calculate_energy_usage,
    calculate_energy_cost,
    weather_recommendations,
)
from models.notification import create_notification
from models.real_estates import RealEstate, register_property
from models.recommendation import Recommendation
from models.recommendation_tips import get_recommendation_tips
from models.user import User
from routers.auth import get_current_user
from schemas.create_real_estate_request import CreateRealEstateRequest
from services.email_sender import send_email_dynamic
from services.weather_api import WeatherService
from services.estimated_energy_and_cost import send_optimization_energy_email
from fastapi import FastAPI



router = APIRouter(prefix="/real-estates", tags=["real-estates"])


# Initialize WeatherService
weather_service = WeatherService(api_key=os.getenv("WEATHER_API_KEY"))
@router.post("/")
async def register_property_route(
    create_real_estate_request: CreateRealEstateRequest,
    db: Session = Depends(db_dependency),
    current_user: User = Depends(get_current_user)
):
    """Register a new real estate property for the current user."""
    new_real_estate = await register_property(create_real_estate_request, db, current_user.id)
    return {"message": "Property created successfully", "property_id": new_real_estate.id}

@router.get("/:real_estate_id/tips")
async def weather_recommendations_route(
    real_estate_id: int,
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format"),
    db: Session = Depends(db_dependency),
    current_user: User = Depends(get_current_user)
):
    """Provide weather-based recommendations for a specific real estate property."""
    real_estate = db.query(RealEstate).filter(
        RealEstate.id == real_estate_id,
        RealEstate.user_id == current_user.id
    ).first()

    if not real_estate:
        raise HTTPException(status_code=404, detail="Real estate not found or access denied.")

    return await weather_recommendations(weather_service, real_estate.location, date, db, current_user.id)

@router.post("/optimize_energy_usage_send_email")
async def optimize_energy_usage_send_email_route(
    background_tasks: BackgroundTasks,
    db: Session = Depends(db_dependency),
    current_user: User = Depends(get_current_user)
) -> Dict:
    """Calculate energy optimization and send detailed email to the user."""
    real_estate = db.query(RealEstate).filter(RealEstate.user_id == current_user.id).first()
    if not real_estate:
        raise HTTPException(status_code=404, detail="No real estate found.")

    square_area = real_estate.square_area
    insulation_quality = real_estate.insulation_quality
    year_built = real_estate.year_built
    energy_source = real_estate.energy_source or "electricity"

    energy_usage = await calculate_energy_usage(square_area, insulation_quality, year_built)
    estimated_cost = await calculate_energy_cost(energy_usage, energy_source)

    recommendation = Recommendation(
        category="Energy Optimization",
        message=f"Estimated daily cost: {estimated_cost:.2f} €.",
        estimated_savings=estimated_cost,
        user_id=current_user.id,
        real_estate_id=real_estate.id
    )
    db.add(recommendation)
    db.commit()

    user_data = {
        "name": current_user.name,
        "email": current_user.email,
        "user_id": current_user.id,
    }
    real_estate_data = {
        "location": real_estate.location,
        "square_area": square_area,
        "insulation_quality": insulation_quality,
        "year_built": year_built,
    }

    background_tasks.add_task(
        send_optimization_energy_email,
        user_data=user_data,
        real_estate_data=real_estate_data,
        energy_usage=energy_usage,
        estimated_cost=estimated_cost,
        db_session=db,
        real_estate_id=real_estate.id,
        weather_service=weather_service  # Ensure WeatherService is passed
    )

    return {
        "square area": square_area,
        "insulation quality": insulation_quality,
        "year built": year_built,
        "energy source": energy_source,
        "estimated energy usage (kWh)": round(energy_usage, 3),
        "estimated daily cost (€)": round(estimated_cost, 3),
        "message": "Email with energy optimization details will be sent shortly."
    }


