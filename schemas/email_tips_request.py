"""
This module contains Pydantic model definitions for validating and serializing
data related to email tip requests.
"""
from typing import Optional
from pydantic import BaseModel

class EmailTipsRequest(BaseModel):
    """
    Schema for sending energy-saving tips via email.
    """
    recipient: str
    subject: Optional[str] = "Energy-Saving Tips"
