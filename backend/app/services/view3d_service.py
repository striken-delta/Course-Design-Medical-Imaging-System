"""3D 视图业务服务"""

from typing import Optional
from sqlalchemy.orm import Session

from app.repositories.marker_repository import MarkerRepository
from app.repositories.patient_repository import StudyRepository


class View3DService:
    def __init__(self, db: Session):
        self.marker_repo = MarkerRepository(db)
        self.study_repo = StudyRepository(db)

    def get_data(self, study_id: int) -> Optional[dict]:
        study = self.study_repo.get_by_id(study_id)
        if not study:
            return None
        markers = self.marker_repo.get_by_study(study_id)
        return {
            "study_id": study_id,
            "model_url": "/static/models/lung.glb",
            "markers": [{
                "id": m.id, "study_id": m.study_id, "slice_id": m.slice_id,
                "x": m.x, "y": m.y, "z": m.z, "confidence": m.confidence,
                "created_at": m.created_at.isoformat() if m.created_at else "",
            } for m in markers],
        }
