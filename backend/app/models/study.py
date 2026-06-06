"""检查模型"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.db.session import Base


class Study(Base):
    __tablename__ = "studies"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    description = Column(String(256), nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    def __repr__(self):
        return f"<Study(id={self.id}, patient_id={self.patient_id})>"
