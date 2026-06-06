"""患者模型"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.db.session import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    patient_code = Column(String(64), nullable=False, unique=True, index=True)
    gender = Column(String(8), nullable=False, default="unknown")  # male / female / unknown
    age_range = Column(String(16), nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    def __repr__(self):
        return f"<Patient(id={self.id}, code={self.patient_code})>"
