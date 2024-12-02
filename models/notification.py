# notification.py
from datetime import datetime
from sqlalchemy.orm import Session
from models.model import Notification

def create_notification(db: Session, user_id: int, message: str, status: str = "Pending"):
    """
    Creates a notification entry in the config.
    """
    notification = Notification(
        user_id=user_id,
        message=message,
        timestamp=datetime.utcnow(),
        status=status
    )
    db.add(notification)
    db.commit()
    return notification
