from datetime import datetime
from sqlalchemy import Integer, Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from models import Base



class Notification(Base):
    """
    Define Notification table/model, which stores notifications for users.

    This model stores notifications sent to users, including the notification's message,
    timestamp, status (e.g., SMS sent status), and the user it belongs to.
    """
    __tablename__ = 'notifications'

    # Primary key for unique notification identification
    id = Column(Integer, primary_key=True)
    message = Column(String(500), nullable=False, default="read")
    email = Column(String(500), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), nullable=False, default="SMS sent successfully", index=True)

    # Foreign key to associate notification with a user
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship("User", back_populates="notifications")

def create_notification(db_session, user_email: str, message: str, user_id: int):
    """
        Creates and stores a notification in the database.
        Args:
            db_session (Session): Active SQLAlchemy database session.
        Returns:
            Notification: The created notification object, refreshed with its database state.
        """
    notification = Notification(
        email=user_email,
        message=message,
        status="Pending",
        user_id=user_id
    )
    db_session.add(notification)
    db_session.commit()
    db_session.refresh(notification)
    return notification
