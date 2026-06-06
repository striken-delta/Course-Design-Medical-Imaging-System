"""切片数据访问"""

from typing import Optional, Tuple
from sqlalchemy.orm import Session

from app.models.ct_slice import CtSlice


class SliceRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, study_id: int, slice_index: int, file_path: str,
               file_format: str, file_size: int, uploaded_by: int) -> CtSlice:
        s = CtSlice(study_id=study_id, slice_index=slice_index, file_path=file_path,
                     file_format=file_format, file_size=file_size, uploaded_by=uploaded_by)
        self.db.add(s)
        self.db.commit()
        self.db.refresh(s)
        return s

    def get_by_id(self, slice_id: int) -> Optional[CtSlice]:
        return self.db.query(CtSlice).filter(CtSlice.id == slice_id).first()

    def list_slices(self, study_id: Optional[int] = None,
                    page: int = 1, page_size: int = 20) -> Tuple[list, int]:
        q = self.db.query(CtSlice)
        if study_id:
            q = q.filter(CtSlice.study_id == study_id)
        total = q.count()
        items = q.order_by(CtSlice.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
        return items, total

    def count_in_range(self, date_from: Optional[str] = None, date_to: Optional[str] = None) -> int:
        q = self.db.query(CtSlice)
        if date_from:
            q = q.filter(CtSlice.uploaded_at >= date_from)
        if date_to:
            q = q.filter(CtSlice.uploaded_at <= date_to + "T23:59:59")
        return q.count()
