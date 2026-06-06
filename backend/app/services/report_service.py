"""报告聚合业务服务"""

from typing import Optional, Tuple
from sqlalchemy.orm import Session

from app.repositories.slice_repository import SliceRepository
from app.repositories.prediction_repository import PredictionRepository
from app.repositories.review_repository import ReviewRepository
from app.repositories.patient_repository import PatientRepository, StudyRepository
from app.repositories.marker_repository import MarkerRepository
from app.models.prediction import Prediction
from app.models.patient import Patient
from app.models.study import Study
from app.models.ct_slice import CtSlice
from app.models.review import Review
from app.core.errors import ErrorCode


class ReportService:
    def __init__(self, db: Session):
        self.db = db
        self.slice_repo = SliceRepository(db)
        self.pred_repo = PredictionRepository(db)
        self.review_repo = ReviewRepository(db)
        self.patient_repo = PatientRepository(db)
        self.study_repo = StudyRepository(db)
        self.marker_repo = MarkerRepository(db)

    def search_reports(
        self, patient_code: Optional[str] = None,
        date_from: Optional[str] = None, date_to: Optional[str] = None,
        label: Optional[str] = None, review_status: Optional[str] = None,
        page: int = 1, page_size: int = 20,
    ) -> Tuple[list, int]:
        """多条件联合检索报告"""
        # 用 ORM join 聚合 patient → study → slice → prediction → review
        q = self.db.query(
            Prediction.id.label("prediction_id"),
            Patient.patient_code, Patient.id.label("patient_id"),
            Patient.gender, Patient.age_range,
            Study.id.label("study_id"),
            CtSlice.id.label("slice_id"), CtSlice.slice_index, CtSlice.file_path.label("slice_file_path"),
            Prediction.label, Prediction.confidence, Prediction.model_version,
            Prediction.inference_time_ms, Prediction.heatmap_path, Prediction.created_at,
        ).join(CtSlice, Prediction.slice_id == CtSlice.id) \
         .join(Study, CtSlice.study_id == Study.id) \
         .join(Patient, Study.patient_id == Patient.id)

        if patient_code:
            q = q.filter(Patient.patient_code.like(f"%{patient_code}%"))
        if date_from:
            q = q.filter(Prediction.created_at >= date_from)
        if date_to:
            q = q.filter(Prediction.created_at <= date_to + "T23:59:59")
        if label:
            q = q.filter(Prediction.label == label)

        total = q.count()
        rows = q.order_by(Prediction.id.desc()).offset((page - 1) * page_size).limit(page_size).all()

        items = []
        for r in rows:
            has_r = self.review_repo.has_review(r.prediction_id)
            latest_r = self.review_repo.get_latest(r.prediction_id)
            # 按 review_status 过滤
            if review_status == "unreviewed" and has_r:
                continue
            if review_status == "reviewed" and not has_r:
                continue

            items.append({
                "prediction_id": r.prediction_id,
                "patient_code": r.patient_code, "patient_id": r.patient_id,
                "gender": r.gender, "age_range": r.age_range,
                "study_id": r.study_id, "slice_id": r.slice_id,
                "slice_index": r.slice_index,
                "slice_file_path": ("/uploads/" + r.slice_file_path) if r.slice_file_path and not r.slice_file_path.startswith("/") else r.slice_file_path,
                "label": r.label, "confidence": r.confidence,
                "model_version": r.model_version, "inference_time_ms": r.inference_time_ms,
                "heatmap_path": r.heatmap_path,
                "review_status": "reviewed" if has_r else "unreviewed",
                "review_label": latest_r.review_label if latest_r else None,
                "corrected_label": latest_r.corrected_label if latest_r else None,
                "created_at": r.created_at.isoformat() if r.created_at else "",
            })

        return items, total

    def get_report_detail(self, prediction_id: int):
        """获取报告详情"""
        pred = self.pred_repo.get_by_id(prediction_id)
        if not pred:
            return None

        s = self.slice_repo.get_by_id(pred.slice_id)
        if not s:
            return None

        study = self.study_repo.get_by_id(s.study_id)
        if not study:
            return None

        patient = self.patient_repo.get_by_id(study.patient_id)
        if not patient:
            return None

        latest_review = self.review_repo.get_latest(prediction_id)
        review_history = self.review_repo.get_by_prediction(prediction_id)
        markers = self.marker_repo.get_by_study(study.id)

        return {
            "prediction": self._pred_to_dict(pred),
            "slice": self._slice_to_dict(s),
            "study": self._study_to_dict(study),
            "patient": self._patient_to_dict(patient),
            "latest_review": self._review_to_dict(latest_review) if latest_review else None,
            "review_history": [self._review_to_dict(r) for r in review_history],
            "markers_summary": [self._marker_to_dict(m) for m in markers],
        }

    # helpers
    def _pred_to_dict(self, p: Prediction) -> dict:
        return {"id": p.id, "slice_id": p.slice_id, "label": p.label,
                "confidence": p.confidence, "model_version": p.model_version,
                "inference_time_ms": p.inference_time_ms, "heatmap_path": p.heatmap_path,
                "created_at": p.created_at.isoformat() if p.created_at else ""}

    def _slice_to_dict(self, s: CtSlice) -> dict:
        fp = s.file_path
        return {"id": s.id, "study_id": s.study_id, "slice_index": s.slice_index,
                "file_path": ("/uploads/" + fp) if fp and not fp.startswith("/") else fp,
                "file_format": s.file_format, "file_size": s.file_size,
                "uploaded_at": s.uploaded_at.isoformat() if s.uploaded_at else ""}

    def _study_to_dict(self, s: Study) -> dict:
        return {"id": s.id, "patient_id": s.patient_id, "description": s.description,
                "created_at": s.created_at.isoformat() if s.created_at else ""}

    def _patient_to_dict(self, p: Patient) -> dict:
        return {"id": p.id, "patient_code": p.patient_code, "gender": p.gender,
                "age_range": p.age_range, "created_at": p.created_at.isoformat() if p.created_at else ""}

    def _review_to_dict(self, r: Review) -> dict:
        return {"id": r.id, "prediction_id": r.prediction_id,
                "review_label": r.review_label,
                "corrected_label": r.corrected_label,
                "comment": r.comment,
                "reviewed_by": r.reviewed_by,
                "reviewed_at": r.reviewed_at.isoformat() if r.reviewed_at else ""}

    def _marker_to_dict(self, m) -> dict:
        return {"id": m.id, "study_id": m.study_id, "slice_id": m.slice_id,
                "x": m.x, "y": m.y, "z": m.z, "confidence": m.confidence,
                "created_at": m.created_at.isoformat() if m.created_at else ""}
