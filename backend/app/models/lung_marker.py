"""3D 标记模型"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from app.db.session import Base


class Lung3DMarker(Base):
    __tablename__ = "lung_3d_markers"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    study_id = Column(Integer, ForeignKey("studies.id"), nullable=False, index=True)
    slice_id = Column(Integer, ForeignKey("ct_slices.id"), nullable=True)
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    z = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Lung3DMarker(id={self.id}, study_id={self.study_id})>"
