import os
import uvicorn
import logging
import dotenv
from fastapi import FastAPI, HTTPException, status
from starlette.staticfiles import StaticFiles
from config.database import engine
from models import model
from routers.router import router
from routers import auth

# Load environment variables
dotenv.load_dotenv()

# Initialize the app and logger
app = FastAPI()
logger = logging.getLogger("main")
logging.basicConfig(level=logging.INFO)


# Retrieve API keys from .env
MAILERSEND_API_KEY = os.getenv("MAILERSEND_API_KEY")
API_KEY = os.getenv("WEATHER_API_KEY")

if not MAILERSEND_API_KEY:
    raise ValueError("MailerSend API key is not set. Check your .env file.")

# Static file mounting
app.mount("/public", StaticFiles(directory="public"), name="public")

# Create config tables
try:
    model.Base.metadata.create_all(bind=engine)
except Exception as e:
    logger.error(f"Error initializing database_db tables: {str(e)}")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Database initialization error.")

# Include routers - user registration endpoints first
app.include_router(auth.router)  # Include the auth router first for user registration and login
app.include_router(router)  # Include the main router with routes

@app.get("/")
async def root():
    return {"message": "Welcome to the Real Estate Energy Efficiency Advisory App with User Registration API and JWT"}


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)

