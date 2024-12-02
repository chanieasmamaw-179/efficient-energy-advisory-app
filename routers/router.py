import os
from asyncio import to_thread
from asyncio.log import logger

from fastapi import APIRouter, Depends, Query, BackgroundTasks, HTTPException
from typing import Dict, Optional
from sqlalchemy.orm import Session
from starlette.responses import FileResponse

from config.dependencies import db_dependency
from models import model
from models.recomendation_tips import get_recommendation_tips
from models.model import User, Recommendation
from models.real_estate import register_property
from models.energy_cost_estimation_engine import calculate_energy_usage, calculate_energy_cost, weather_recommendations
from models.notification import create_notification
from routers.auth import get_current_user
from services.email_sender import send_email_dynamic
from services.weather_api import WeatherService
from schemas.create_real_estate_request import CreateRealEstateRequest

router = APIRouter()

# Initialize WeatherService
weather_service = WeatherService(api_key=os.getenv("WEATHER_API_KEY"))

@router.post("/real-estates")
async def register_property_route(
        create_real_estate_request: CreateRealEstateRequest,
        db: Session = Depends(db_dependency),
        current_user: User = Depends(get_current_user)
):
    new_real_estate = await register_property(create_real_estate_request, db, current_user.id)
    return {"message": "Property created successfully", "property_id": new_real_estate.id}

@router.get("/weather-tips")
async def weather_recommendations_route(
    city: str,
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format"),
    db: Session = Depends(db_dependency),
    current_user: User = Depends(get_current_user)
):
    return await weather_recommendations(weather_service, city, date, db, current_user.id)

@router.post("/optimize_energy_usage_send_email")
async def optimize_energy_usage_send_email_route(
        background_tasks: BackgroundTasks,
        db: Session = Depends(db_dependency),
        current_user: User = Depends(get_current_user)
) -> Dict:
    # Fetch user real estate
    real_estate = db.query(model.RealEstate).filter(model.RealEstate.user_id == current_user.id).first()
    if not real_estate:
        raise HTTPException(status_code=404, detail="No real estate found.")

    # Calculate energy optimization
    square_area = real_estate.square_area
    insulation_quality = real_estate.insulation_quality
    year_built = real_estate.year_built
    energy_source = real_estate.energy_source or "electricity"

    energy_usage = await calculate_energy_usage(square_area, insulation_quality, year_built)
    estimated_cost = await calculate_energy_cost(energy_usage, energy_source)

    # Save recommendation to the config
    recommendation = Recommendation(
        category="Energy Optimization",
        message=f"Estimated daily cost: {estimated_cost:.2f} €.",
        estimated_savings=estimated_cost,
        user_id=current_user.id,
        real_estate_id=real_estate.id
    )
    db.add(recommendation)
    db.commit()

    # Extract necessary data for background task
    user_data = {
        "name": current_user.name,
        "email": current_user.email,
    }
    real_estate_data = {
        "location": real_estate.location,
        "square_area": square_area,
        "insulation_quality": insulation_quality,
        "year_built": year_built,
    }

    # Add email-sending task to background tasks
    background_tasks.add_task(
        send_optimization_email,
        user_data=user_data,
        real_estate_data=real_estate_data,
        energy_usage=energy_usage,
        estimated_cost=estimated_cost,
        db_session=db
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

# Background task function
async def send_optimization_email(
        user_data: Dict,
        real_estate_data: Dict,
        energy_usage: float,
        estimated_cost: float,
        db_session: Session
):
    city = real_estate_data["location"] or "Unknown"
    weather_data = weather_service.get_weather(city)
    if not weather_data:
        raise HTTPException(status_code=404, detail="City not found or API error.")

    temp = weather_data["main"]["temp"]
    weather_tips = get_recommendation_tips(temp).split('\n')

    # Prepare email content
    subject = "Your Personalized Energy Optimization Update"
    formatted_weather_tips = "<ul>" + "\n".join(f"<li>{tip}</li>" for tip in weather_tips) + "</ul>"
    html_content = f"""
    <h1>Hello {user_data['name']},</h1>
    <p>Your personalized energy advisory report:</p>
    <ul>
        <li><b>Square area:</b> {real_estate_data['square_area']} m²</li>
        <li><b>Insulation quality:</b> {real_estate_data['insulation_quality']}</li>
        <li><b>Year built:</b> {real_estate_data['year_built']}</li>
        <li><b>Estimated energy usage:</b> {energy_usage:.3f} kWh</li>
        <li><b>Estimated daily cost:</b> {estimated_cost:.3f} €</li>
        <li><b>Temperature at location:</b> {temp} °C</li>
    </ul>
    <h2>Weather Tips:</h2>
    {formatted_weather_tips}
    <p>Thank you for using our service!</p>
    """
    text_content = f"""
    Hello {user_data['name']},

    Your personalized energy advisory report:
    - Square area: {real_estate_data['square_area']} m²
    - Insulation quality: {real_estate_data['insulation_quality']}
    - Year built: {real_estate_data['year_built']}
    - Estimated energy usage: {energy_usage:.3f} kWh
    - Estimated daily cost: {estimated_cost:.3f} €
    - Temperature at location: {temp} °C

    Weather Tips:
    {', '.join(weather_tips)}

    Thank you for using our efficient energy advisory service !
    """

    # Define sender and recipient
    sender = {"name": "Efficient Energy Advisory", "email": "MS_vDTC8L@trial-pq3enl6wpk842vwr.mlsender.net"}
    recipient = {"name": user_data['name'], "email": user_data['email']}

    # Create a notification for the email
    notification = create_notification(db_session, user_data['email'], f"Email scheduled for {recipient['email']}")

    # Send email
    try:
        logger.info(f"Sending optimization email to {recipient['email']}")
        await to_thread(
            send_email_dynamic,
            sender=sender,
            recipient=recipient,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
        notification.status = "Sent"
        logger.info(f"Email sent to {recipient['email']}")
    except Exception as e:
        notification.status = "Failed"
        logger.error(f"Error sending email to {recipient['email']}: {e}")
    finally:
        db_session.add(notification)
        db_session.commit()

@router.get("/favicon.ico")
def favicon():
    """
    This is the design symbol of our Energy advisory app
    """
    return FileResponse("public/favicon.ico")
