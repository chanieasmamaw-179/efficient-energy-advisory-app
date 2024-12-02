from typing import List
from datetime import datetime

# Weather tips based on temperature
def get_recommendation_tips(temp: float) -> str:
    # Ensure temp is a valid float before proceeding
    if not isinstance(temp, (int, float)):
        raise ValueError("Temperature must be a number.")

    tips: List[str] = []  # Explicitly define the list type

    # Get current time to determine sunrise and sunset
    current_time = datetime.now()
    sunrise_time = datetime(current_time.year, current_time.month, current_time.day, 6, 0)  # Example: 6 AM sunrise
    sunset_time = datetime(current_time.year, current_time.month, current_time.day, 18, 0)  # Example: 6 PM sunset

    if temp > 30.0:
        tips.append("Consider setting your AC to 24°C for efficiency and reducing energy consumption.")
        tips.append("Close blinds and curtains during the hottest part of the day to reduce heat indoors.")
        tips.append("Drink plenty of water to stay hydrated and avoid overheating.")
        tips.append("Wear light, breathable clothing to stay cool and reduce the need for excessive air conditioning.")
        tips.append("Avoid using heat-generating appliances like ovens and stoves during peak heat hours.")
        tips.append("If possible, spend time in a cooler, shaded area or outdoors during cooler parts of the day.")
        tips.append(
            "Use a fan to circulate air if AC isn't available, and ensure your fan is positioned to create cross-ventilation.")
        tips.append(
            "Ensure your AC or cooling system is well-maintained, and consider replacing old filters to increase efficiency.")
        tips.append(
            "Check insulation in windows, walls, and doors to prevent cool air from escaping, and upgrade insulation if necessary.")
        tips.append(
            "If your home is equipped with smart thermostats, program them to optimize cooling during peak hours.")

    # Cold weather tips (temp < 10.0°C)
    elif temp < 10.0:
        tips.append("Lower your thermostat to save energy, and set it to 18°C when you're not at home or asleep.")
        tips.append("Seal any window drafts with weatherstripping or use draft stoppers to keep warmth inside.")
        tips.append(
            "Wear layers to stay warm and reduce the need for heating. Wool and fleece are excellent for insulation.")
        tips.append("Use thermal curtains or heavy drapes to trap warmth inside and block the cold air from entering.")
        tips.append(
            "Keep your home’s heating system well-maintained, and consider getting it serviced before winter to improve efficiency.")
        tips.append("Use a space heater in rooms you frequent, but ensure it's energy-efficient and safe to use.")
        tips.append(
            "Cook or bake to add warmth to your home while preparing meals—this helps reduce the need for additional heating.")
        tips.append("Consider using electric blankets or heated mattress pads for additional warmth in the bedroom.")
        tips.append(
            "Upgrade insulation in your home, especially in the attic and basement, where heat loss is most significant.")
        tips.append("If your home has a fireplace, ensure it's properly sealed when not in use to prevent heat loss.")

    # Moderate weather tips (temp between 10.0°C and 30.0°C)
    else:
        tips.append("Open windows to cool down naturally, especially during the early morning or late evening.")
        tips.append("Use ceiling fans instead of AC to save energy and ensure proper air circulation.")
        tips.append(
            "Take advantage of natural sunlight by opening blinds during the day and closing them at night to keep warmth inside.")
        tips.append("Switch to energy-efficient LED bulbs that emit less heat and consume less energy.")
        tips.append(
            "Consider using natural fabrics like cotton for bedding to stay comfortable and reduce reliance on climate control.")
        tips.append(
            "Turn off lights and electronics when not in use to save energy and prevent excess heat in your home.")
        tips.append(
            "If your home has smart devices, set them to optimize energy usage, like smart thermostats or lighting systems.")

    # Daylight-related tips based on sunrise and sunset
    if current_time < sunrise_time:
        tips.append(
            "Turn off lamps and other lights to save energy, as the sun is rising and natural light is increasing.")
    elif current_time > sunset_time:
        tips.append("Turn off lamps and lights since natural light is available.")
    else:
        tips.append("Take advantage of natural light and turn off lamps during the day to reduce energy consumption.")

    # Return tips with 1.5 line spacing by adding an extra newline
    return "\n".join(tips)  # Adding an extra newline between each tip for 1.5 line spacing
