"""预测模型"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from app.db.session import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    slice_id = Column(Integer, ForeignKey("ct_slices.id"), nullable=False, index=True)
    label = Column(String(16), nullable=False)  # nodule / non_nodule
    confidence = Column(Float, nullable=False)
    model_version = Column(String(32), nullable=False)
    inference_time_ms = Column(Integer, nullable=False)
    heatmap_path = Column(String(512), nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Prediction(id={self.id}, label={self.label}, confidence={self.confidence})>"
