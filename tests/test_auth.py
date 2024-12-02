import pytest
from fastapi.testclient import TestClient
from routers.auth import create_access_token
from models.model import User
from sqlalchemy.orm import Session
from unittest.mock import MagicMock

# Mock dependencies
@pytest.fixture
def mock_db():
    """
    Fixture to mock the config session.
    """
    mock_session = MagicMock(spec=Session)
    return mock_session

@pytest.fixture
def test_client():
    """
    Fixture to provide a test client for the FastAPI app.
    """
    return TestClient(app)

# Sample test data
TEST_USER = {
    "full_name": "Test User",
    "email": "testuser@example.com",
    "password": "SecureP@ssword1",
    "confirm_password": "SecureP@ssword1",
    "phone_number": "+12345678901",
}

@pytest.fixture
def mock_user_in_db(mock_db):
    """
    Fixture to simulate an existing user in the config.
    """
    user = User(
        name="Existing User",
        email="existinguser@example.com",
        hash_password="$2b$12$1234567890123456789012",  # Fake bcrypt hash
        phone_number="+12345678902",
    )
    mock_db.query.return_value.filter.return_value.first.return_value = user
    return user

# Test cases
def test_user_registration_success(test_client, mock_db):
    """
    Test successful user registration.
    """
    response = test_client.post("/user_registration/", json=TEST_USER)
    assert response.status_code == 201
    assert response.json()["message"] == "User created successfully"

def test_user_registration_email_exists(test_client, mock_db, mock_user_in_db):
    """
    Test registration with an email that already exists in the config.
    """
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user_in_db

    response = test_client.post("/user_registration/", json=TEST_USER)
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered."

def test_user_registration_invalid_phone_number(test_client):
    """
    Test registration with an invalid phone number format.
    """
    invalid_user_data = TEST_USER.copy()
    invalid_user_data["phone_number"] = "12345"  # Invalid phone number

    response = test_client.post("/user_registration/", json=invalid_user_data)
    assert response.status_code == 422  # Validation error
    assert "phone_number" in response.text

def test_login_success(test_client, mock_user_in_db, mock_db):
    """
    Test successful user login with correct credentials.
    """
    mock_user_in_db.hash_password = "$2b$12$COrrectPa/sswordHash"  # Fake bcrypt hash

    response = test_client.post(
        "/user_registration/token",
        data={"username": "existinguser@example.com", "password": "CorrectPassword"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_failure_wrong_password(test_client, mock_user_in_db, mock_db):
    """
    Test login failure with incorrect password.
    """
    response = test_client.post(
        "/user_registration/token",
        data={"username": "existinguser@example.com", "password": "WrongPassword"},
    )
    assert response.status_code == 200
    assert response.json()["error"] == "Authentication Failed"

def test_login_failure_user_not_found(test_client, mock_db):
    """
    Test login failure when user does not exist.
    """
    mock_db.query.return_value.filter.return_value.first.return_value = None  # No user

    response = test_client.post(
        "/user_registration/token",
        data={"username": "nonexistent@example.com", "password": "AnyPassword"},
    )
    assert response.status_code == 200
    assert response.json()["error"] == "Authentication Failed"

def test_token_validation_success(mock_user_in_db, mock_db):
    """
    Test successful token schemas.
    """
    token = create_access_token({"sub": "existinguser@example.com"})
    headers = {"Authorization": f"Bearer {token}"}

    response = test_client.get("/user_registration/protected-endpoint", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == "existinguser@example.com"

def test_token_validation_expired_token(test_client, mock_db):
    """
    Test token schemas with an expired token.
    """
    expired_token = create_access_token({"sub": "existinguser@example.com"}, expires_delta=-1)
    headers = {"Authorization": f"Bearer {expired_token}"}

    response = test_client.get("/user_registration/protected-endpoint", headers=headers)
    assert response.status_code == 401
    assert response.json()["detail"] == "Token has expired."

def test_token_validation_invalid_token(test_client, mock_db):
    """
    Test token schemas with an invalid token.
    """
    headers = {"Authorization": "Bearer InvalidToken"}

    response = test_client.get("/user_registration/protected-endpoint", headers=headers)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token."
