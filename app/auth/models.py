from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime, Boolean
from app.core.database import Base
import enum
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import uuid


class UserRole(str, enum.Enum):
    admin = "admin"
    user = "user"


class User(Base):
  __tablename__ = "users"

  id = Column(Integer, primary_key=True, index=True)
  name = Column(String, nullable=False)
  email = Column(String, unique=True, nullable=False, index=True)
  hashed_password = Column(String, nullable=False)
  role = Column(Enum(UserRole), nullable=False, default=UserRole.user)


class PasswordResetToken(Base):
  __tablename__ = "password_reset_tokens"

  id = Column(Integer, primary_key=True, index=True)
  user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
  token = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
  expiration_time = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(minutes=30))
  used = Column(Boolean, default=False)

  user = relationship("User")
  