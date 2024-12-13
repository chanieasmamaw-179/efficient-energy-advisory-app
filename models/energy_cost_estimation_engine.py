"""
Estimating the energy consumed and return to cost from weather
 API and provided weather tips and report.
"""
# Standard library import
from datetime import datetime
# Third-party imports
from fastapi import HTTPException
from sqlalchemy.orm import Session
# Local imports
from services.weather_api import WeatherService
from models.weather_recommendation import WeatherBasedRecommendation
#from models.recommendation import Recommendation
def get_recommendation_tips(temperature: float) -> str:
    """
    Returns tips based on the given temperature.
    """
    if temperature > 30:
        return "Consider air conditioning or ventilation."
    elif temperature > 20:
        return "Optimal weather, no changes needed."
    elif temperature > 10:
        return "Consider heating to stay comfortable."
    else:
        return "Ensure your insulation is up to standard."

async def calculate_energy_usage(square_area: int, insulation_quality:
str, year_built: int) -> float:
    """
    Calculate energy usage based on real estate factors.
    """
    baseline_consumption = 4  # kWh per square area per month in EU (2024)
    insulation_factor = ({"poor": 1.2, "average": 1.0, "good": 0.8}
                         .get(insulation_quality.lower(), 1.0))
    age_factor = 1 + (2024 - year_built) / 100  # Aging factor, the older house will consume more energy than the new
    return square_area * baseline_consumption * insulation_factor * age_factor

async def calculate_energy_cost(energy_consumption: float, energy_source: str) -> float:
    """
    Calculate energy cost based on energy consumption and source.
    """
    energy_rates = {"electrireal_estate_id": 0.28, "natural_gas": 0.09, "solar": 0.02} # rating is in EU 2024
    rate = energy_rates.get(energy_source.lower(), 0.28)  # Default to electrireal_estate_id
    return energy_consumption * rate / 30  # for daily calculations

async def weather_recommendations(weather_service: WeatherService, city:
str, date: str, db: Session, user_id: int):
    """
    Provide weather-based recommendations and tips.
    """
    weather_data = weather_service.get_weather(city)
    if not weather_data:
        raise HTTPException(status_code=404, detail="real_estate_id not found or API error.")

    specified_date = datetime.strptime(date, "%Y-%m-%d").date() if date else datetime.now().date()
    temp = weather_data["main"]["temp"]
    tips = get_recommendation_tips(temp)

    # Save to config
    weather_recommendation = WeatherBasedRecommendation(
        message=f"Recommended action for weather in {city}",
        temperature_condition=f"{temp}°C",
        weather_tips=tips,
        user_id=user_id
    )
    db.add(weather_recommendation)
    db.commit()

    return {"city": city, "date": specified_date, "temperature": temp, "tips": tips.split("\n")}
