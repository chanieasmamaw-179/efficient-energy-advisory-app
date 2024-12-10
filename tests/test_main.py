import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
#from main import app
from config.database import Base
from routers.auth import create_access_token
from models.model import User

# Setup for test config
DATABASE_URL = "sqlite:///./energy_saving_app.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

# Dependency override for testing
def override_db_dependency():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides["db_dependency"] = override_db_dependency

# Test client
client = TestClient(app)

# Test data setup
@pytest.fixture(scope="module")
def test_user():
    return User(
        id=1,
        name="Test User",
        email="testuser@example.com",
        password="testpassword"  # Assuming passwords are hashed in production
    )

@pytest.fixture(scope="module")
def test_access_token(test_user):
    return create_access_token({"sub": test_user.email})

# Test endpoints
def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Real Estate Energy Efficiency Advisory App with User Registration API and JWT"}

def test_register_property_route(test_access_token):
    headers = {"Authorization": f"Bearer {test_access_token}"}
    payload = {
        "location": "Test real_estate_id",
        "square_area": 100,
        "insulation_quality": "Good",
        "year_built": 2000,
        "energy_source": "electrireal_estate_id"
    }
    response = client.post("/real-estates", json=payload, headers=headers)
    assert response.status_code == 200
    assert "property_id" in response.json()

def test_weather_recommendations_route(test_access_token):
    headers = {"Authorization": f"Bearer {test_access_token}"}
    response = client.get("/weather-tips?real_estate_id=Testreal_estate_id", headers=headers)
    assert response.status_code == 200
    assert "tips" in response.json()

def test_optimize_energy_usage_send_email_route(test_access_token):
    headers = {"Authorization": f"Bearer {test_access_token}"}
    response = client.post("/optimize_energy_usage_send_email", headers=headers)
    assert response.status_code == 200
    assert "estimated energy usage (kWh)" in response.json()
    assert "message" in response.json()

# Test background task (mocking)
from unittest.mock import patch

@patch("main.send_optimization_email")
def test_optimize_energy_usage_email_task(mock_send_email, test_access_token):
    mock_send_email.return_value = None  # Mocking send email as no-op
    headers = {"Authorization": f"Bearer {test_access_token}"}
    response = client.post("/optimize_energy_usage_send_email", headers=headers)
    assert response.status_code == 200
    assert mock_send_email.called
