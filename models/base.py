"""
Base module for SQLAlchemy ORM models.
This module defines the `Base` class, which serves as the foundational
class for all ORM models in the project. Models should inherit from this
`Base` class to integrate seamlessly with SQLAlchemy's ORM functionality.
"""
from sqlalchemy.ext.declarative import declarative_base
# Base class for all SQLAlchemy models
Base = declarative_base()
