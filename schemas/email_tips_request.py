# pydantic_validation.py

from pydantic import BaseModel, Field
from typing import Optional

class EmailTipsRequest(BaseModel):
    recipient: str
    subject: Optional[str] = "Energy-Saving Tips"
