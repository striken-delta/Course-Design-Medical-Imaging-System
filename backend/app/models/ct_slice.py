"""切片模型"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.db.session import Base


class CtSlice(Base):
    __tablename__ = "ct_slices"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    study_id = Column(Integer, ForeignKey("studies.id"), nullable=False, index=True)
    slice_index = Column(Integer, nullable=False, default=0)
    file_path = Column(String(512), nullable=False)
    file_format = Column(String(8), nullable=False)  # png / jpg / jpeg
    file_size = Column(Integer, nullable=False)
    uploaded_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    def __repr__(self):
        return f"<CtSlice(id={self.id}, study_id={self.study_id}, index={self.slice_index})>"
