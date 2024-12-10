"""
Main application setup and initialization for the FastAPI project.
"""
# Standard library imports
# Provides functions to interact with the operating system
import os
import logging  # Used for configuring and managing application logging

# Third-party imports
import dotenv  # Used to load environment variables from a .env file into the application
# FastAPI framework and related utilities for handling exceptions and HTTP status codes
from fastapi import FastAPI, HTTPException, status
# Enables serving static files in FastAPI
from starlette.staticfiles import StaticFiles
# Allows scheduling tasks to run in the background
from apscheduler.schedulers.background import BackgroundScheduler

# Local application imports
from config import database  # Configuration module for database setup and connections
# Specific database functions for handling engine creation and cleanup tasks
from config.database import engine, clean_up_old_records
# Router module handling energy estimation routes
from routers.energy_estimations import router
from routers import auth  # Router module for authentication-related routes

app = FastAPI()
# Include your router with its prefix
app.include_router(router)

# Load environment variables
dotenv.load_dotenv()

# Initialize the app and logger
app = FastAPI()
logger = logging.getLogger("main")
logging.basicConfig(level=logging.INFO)


scheduler = BackgroundScheduler()
# Retrieve API keys from .env
MAILERSEND_API_KEY = os.getenv("MAILERSEND_API_KEY")
API_KEY = os.getenv("WEATHER_API_KEY")

if not MAILERSEND_API_KEY:
    raise ValueError("MailerSend API key is not set. Check your .env file.")

# Static file mounting
app.mount("/public", StaticFiles(directory="public"), name="public")

# Create config tables

try:
    database.Base.metadata.create_all(bind=engine)
except Exception as e:
    logger.error("Error initializing database_db tables %s:", str(e))
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Database initialization error.")

# Include routers - user registration endpoints first
app.include_router(auth.router)  # Include the auth router first for user registration and login
app.include_router(router)  # Include the main router with routes

@app.get("/", include_in_schema=False)
async def root():
    """
    Home pages: Welcome messages
    """
    return {"message": "Welcome to the Real Estate Energy Efficiency "
                       "Advisory App with User Registration API and JWT"}


@app.on_event("startup")
def start_cleanup_scheduler():
    """"
        Starts the scheduled cleanup task when the FastAPI app starts.
        The task is set to run montly on Sunday at midnight.
    """
    scheduler.add_job(clean_up_old_records, "cron", day_of_week="sun", hour=0, minute=0)
    scheduler.start()


@app.on_event("shutdown")
def stop_cleanup_scheduler():
    """
        Stops the scheduled cleanup task when the FastAPI app shuts down.
    """
    scheduler.shutdown()


@app.get("/favicon.ico")
async def favicon():
    """
    Logo for the app
    """
    return FileResponse("static/favicon.ico")



