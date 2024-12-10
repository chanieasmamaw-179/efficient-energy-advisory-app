# Standard library imports
from asyncio import to_thread
from asyncio.log import logger
from typing import Dict

# Third-party imports
from fastapi import HTTPException
from sqlalchemy.orm import Session

# Local application imports
from models.notification import create_notification
from models.recommendation_tips import get_recommendation_tips
from services.email_sender import send_email_dynamic
from services.weather_api import WeatherService


# Background task function
async def send_optimization_energy_email(
    user_data: Dict,
    real_estate_data: Dict,
    energy_usage: float,
    estimated_cost: float,
    db_session: Session,
    real_estate_id: int,
    weather_service: WeatherService
):
    city = real_estate_data["location"] or "Unknown"
    weather_data = weather_service.get_weather(city)
    if not weather_data:
        raise HTTPException(status_code=404, detail="City not found or API error.")

    temp = weather_data["main"]["temp"]
    weather_tips = get_recommendation_tips(temp).split('\n')

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

    Thank you for using our efficient energy advisory service!
    """

    sender = {"name": "Efficient Energy Advisory", "email": "MS_vDTC8L@trial-pq3enl6wpk842vwr.mlsender.net"}
    recipient = {"name": user_data['name'], "email": user_data['email']}

    notification = create_notification(
        db_session,
        user_email=user_data['email'],
        message=f"Email scheduled for {recipient['email']}",
        user_id=user_data['user_id'],
    )
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
