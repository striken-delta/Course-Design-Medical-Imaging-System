"""用户模型"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    username = Column(String(32), nullable=False, unique=True, index=True)
    password_hash = Column(String(128), nullable=False)
    role = Column(String(16), nullable=False, default="patient")  # doctor / admin / patient
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"
