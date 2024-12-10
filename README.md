# Real Estate Energy Efficiency Advisory App

## Overview
This project provides an energy efficiency advisory app aimed at helping users assess and improve their home's energy efficiency. The app offers personalized recommendations based on user inputs, such as home details and energy usage.

## Features
- **User Registration**: Users can create accounts with email, password, and phone number.
- **Authentication**: Login via JWT tokens for secure access.
- **Energy Assessment**: Users can input property data to receive energy-saving recommendations.
- **Notifications**: Users receive notifications based on their preferences.
## Real Estate Management
    Register and manage real estate properties.
    Associate properties with authenticated users.
    Input validations using Pydantic models.

## Weather-Based Recommendations
    Fetch real-time weather data for a user’s real_estate_id.
    Provide actionable recommendations based on weather conditions.

## Energy Consumption and Cost Estimation
    Estimate energy consumption based on property attributes like area, insulation quality, and year built.
    Calculate daily costs based on energy source and estimated consumption.

## Personalized Email Notifications
    Generate detailed energy advisory emails for users.
    Includes weather recommendations and property energy consumption estimates.

## Technologies Used
    Backend Framework: FastAPI
    Database: SQLAlchemy ORM with support for relational database models
    Email API: MailerSend
    Weather API: Integration for real-time weather data
    Static Files: Starlette's StaticFiles for serving static assets


## API Endpoints
1. Root Endpoint
    GET /
    Returns a welcome message.
2. Real Estate Management
    POST /real-estates
    Registers a new property for the authenticated user.
3. Weather Recommendations
    GET /weather-tips
    Provides weather-based energy tips for a specific real_estate_id and optional date.
4. Energy Consumption and Cost Estimation
    POST /estimate_energy_consumption_and_cost
    Estimates the energy consumption and cost for the user's real estate.
5. Email Notifications
    POST /send_email
    Sends a personalized email with energy advisory details to the current user.
6. Favicon
    GET /favicon.ico
    Returns the app’s favicon.

## Environment Variables
Create a .env file in the project root with the following keys:
MAILERSEND_API_KEY=<Your MailerSend API Key>
WEATHER_API_KEY=<Your Weather API Key>
API_KEY_CLOUD_FLARE=<Your Cloudflare API Key>

## Prerequisites
    Python 3.8+
    Installed dependencies from requirements.txt
## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/chanieasmamaw-179/Home-Energy-Enficiency-Advisory-app-version-1.0.git
   cd Home-Energy-Efficiency-Advisory-app-version-1.0

2. Install dependencies:

pip install -r requirements.txt

Configuration
Ensure that you have a .env file in the project root with the following variables to hied the keys:

SECRET_KEY=your_secret_key

Usage
1. Run fastAPI:
uvicorn main:app --reload

2. Access the API documentation at:
Access the API documentation at:    to access the SUI and to register the users

3. Access the API documentation:
    Swagger UI: http://127.0.0.1:8000/docs
    ReDoc: http://127.0.0.1:8000/redoc

## Database Setup
    The app uses SQLAlchemy for database management. Ensure the database engine (engine) is correctly
    configured in database.py.
    Create tables automatically by running:
    model.Base.metadata.create_all(bind=engine)

# File Structure

.
├── app/                                   # Root directory for the app code
│   ├── main.py                            # Main application file (FastAPI app initialization)
│   ├── alembic/                           # If using Alembic for database migrations
│   │   ├── env.py                         # Alembic environment configuration
│   │   ├── README.md                      # Documentation for Alembic migrations (optional)
│   │   └── script.py.mako                  # Template for migration scripts (optional)
│   ├── database/                          # Database management and session handling
│   │   └── database.py                    # Database engine and session management
│   ├── users/                             # User authentication and authorization
│   │   ├── auth.py                        # User authentication and JWT logic
│   │   └── dependencies.py                # Dependency injection for current_user, db, etc.
│   ├── models/                            # SQLAlchemy and Pydantic models
│   │   ├── model.py                       # Core models (SQLAlchemy and Pydantic)
│   │   ├── energy_cost_estimation_engine.py  # Logic for energy cost estimation
│   │   ├── notification.py                # Logic for notifications
│   │   ├── pydantic_validation_model.py   # Pydantic validation models
│   │   ├── real_estates.py                # Real estate-related models (for registering properties)
│   │   └── recommendation_tips.py        # Logic for generating energy tips
│   ├── services/                          # External service integrations (e.g., weather, email)
│   │   ├── WeatherAPI.py                  # Weather service integration
│   │   └── email_sender.py                # Dynamic email sending logic
│   ├── static/                            # Directory for static files (e.g., favicon.ico, images)
│   ├── templates/                         # Directory for email or HTML templates (if used)
│   ├── test/                              # Unit tests for the application
│   │   ├── test_main.py                   # Tests for the main application routes
│   │   ├── test_auth.py                   # Tests for user authentication
│   │   ├── test_real_estates.py           # Tests for real estate endpoints
│   │   └── test_email_sender.py           # Tests for email sending functionality
│   └── config/                            # Configuration files (e.g., environment variables)
│       └── .env                           # Environment variables (e.g., API keys, database URIs)
├── requirements.txt                       # Python dependencies
├── README.md                              # Project documentation
└── .gitignore                             # Git ignore file (optional, if using git)




License:
Masterschool, Berlin & Dr. Asmamaw Yehun (Junior Software Engineer) & Ing. Aidan Rudkovskyi (Senior Software Engineer, project mentor, Masterschool) &
Nitzan Smulevici (Senior Software Engineer, Software Engineering Mentor, Masterschool)

License – see the LICENSE file for details.
This README gives a clear overview, installation instructions, and usage details for the project. You can customize
it further to meet your specific needs.

Contact

For issues or inquiries, contact Efficient Energy Advisory at:
Email: MS_T1JOYn@efficientenergyadvisoryapp.org
+4915566400997