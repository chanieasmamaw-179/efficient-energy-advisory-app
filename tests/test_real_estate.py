import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.exc import SQLAlchemyError
from models.real_estate import register_property, CreateRealEstateRequest
from fastapi import HTTPException
from models.model import RealEstate

# Test data
TEST_USER_ID = 1
VALID_REAL_ESTATE_REQUEST = CreateRealEstateRequest(
    square_area=120,
    real_estate_type="Apartment",
    year_built=2005,
    insulation_quality="High",
    energy_source="Solar",
    location="New York",
)

@pytest.fixture
def mock_db_session():
    """
    Fixture to create a mock config session.
    """
    mock_session = MagicMock()
    mock_session.add = MagicMock()
    mock_session.commit = MagicMock()
    mock_session.refresh = MagicMock()
    mock_session.rollback = MagicMock()
    return mock_session

def test_register_property_success(mock_db_session):
    """
    Test successful property registration.
    """
    # Call the function
    response = register_property(
        create_real_estate_request=VALID_REAL_ESTATE_REQUEST,
        db=mock_db_session,
        user_id=TEST_USER_ID,
    )

    # Assertions
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once()
    assert response.square_area == VALID_REAL_ESTATE_REQUEST.square_area
    assert response.real_estate_type == VALID_REAL_ESTATE_REQUEST.real_estate_type
    assert response.year_built == VALID_REAL_ESTATE_REQUEST.year_built
    assert response.insulation_quality == VALID_REAL_ESTATE_REQUEST.insulation_quality
    assert response.energy_source == VALID_REAL_ESTATE_REQUEST.energy_source
    assert response.location == VALID_REAL_ESTATE_REQUEST.location
    assert response.user_id == TEST_USER_ID

def test_register_property_database_error(mock_db_session):
    """
    Test property registration failure due to a config error.
    """
    # Simulate a config error during add or commit
    mock_db_session.commit.side_effect = SQLAlchemyError("Database error")

    # Call the function and expect an HTTPException
    with pytest.raises(HTTPException) as exc_info:
        register_property(
            create_real_estate_request=VALID_REAL_ESTATE_REQUEST,
            db=mock_db_session,
            user_id=TEST_USER_ID,
        )

    # Assertions
    mock_db_session.rollback.assert_called_once()
    assert exc_info.value.status_code == 500
    assert "Error creating property" in exc_info.value.detail

def test_register_property_validation_error():
    """
    Test property registration with invalid input data.
    """
    # Invalid property data (e.g., square_area <= 0)
    invalid_request = CreateRealEstateRequest(
        square_area=0,
        real_estate_type="Apartment",
        year_built=2005,
        insulation_quality="High",
    )

    with pytest.raises(ValueError):
        invalid_request.square_area  # Trigger schemas on field

@patch("real_estate.RealEstate")
def test_register_property_instance_creation(mock_real_estate_model, mock_db_session):
    """
    Test if RealEstate instance is correctly created with provided data.
    """
    # Call the function
    response = register_property(
        create_real_estate_request=VALID_REAL_ESTATE_REQUEST,
        db=mock_db_session,
        user_id=TEST_USER_ID,
    )

    # Assertions
    mock_real_estate_model.assert_called_once_with(
        square_area=VALID_REAL_ESTATE_REQUEST.square_area,
        real_estate_type=VALID_REAL_ESTATE_REQUEST.real_estate_type,
        year_built=VALID_REAL_ESTATE_REQUEST.year_built,
        insulation_quality=VALID_REAL_ESTATE_REQUEST.insulation_quality,
        energy_source=VALID_REAL_ESTATE_REQUEST.energy_source,
        location=VALID_REAL_ESTATE_REQUEST.location,
        user_id=TEST_USER_ID,
    )
