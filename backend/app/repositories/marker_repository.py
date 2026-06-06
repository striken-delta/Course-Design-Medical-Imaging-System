"""3D 标记数据访问"""

from typing import Optional
from sqlalchemy.orm import Session

from app.models.lung_marker import Lung3DMarker


class MarkerRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, study_id: int, slice_id: Optional[int], x: float, y: float, z: float,
               confidence: float) -> Lung3DMarker:
        m = Lung3DMarker(study_id=study_id, slice_id=slice_id, x=x, y=y, z=z, confidence=confidence)
        self.db.add(m)
        self.db.commit()
        self.db.refresh(m)
        return m

    def get_by_study(self, study_id: int) -> list:
        return self.db.query(Lung3DMarker).filter(Lung3DMarker.study_id == study_id).all()
