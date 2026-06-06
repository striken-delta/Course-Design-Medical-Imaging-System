"""
预测数据访问层 — PredictionRepository

封装 predictions 表的 CRUD 与统计查询。
支持标签更新（复核纠正场景）及按日阳性率统计。
"""

from typing import Optional, Tuple
from sqlalchemy.orm import Session

from app.models.prediction import Prediction


class PredictionRepository:
    """AI 预测结果数据访问"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, slice_id: int, label: str, confidence: float,
               model_version: str, inference_time_ms: int,
               heatmap_path: Optional[str] = None) -> Prediction:
        """创建一条 AI 推理预测记录"""
        p = Prediction(slice_id=slice_id, label=label, confidence=confidence,
                        model_version=model_version, inference_time_ms=inference_time_ms,
                        heatmap_path=heatmap_path)
        self.db.add(p)
        self.db.commit()
        self.db.refresh(p)
        return p

    def get_by_id(self, pred_id: int) -> Optional[Prediction]:
        """按 ID 查询单条预测"""
        return self.db.query(Prediction).filter(Prediction.id == pred_id).first()

    def update_label(self, pred_id: int, new_label: str) -> None:
        """
        更新预测标签（复核纠正后调用）

        当医生复核选择 corrected 时，将预测标签更新为医生指定的正确值。
        例如 AI 误判 nodule → 医生纠正为 non_nodule，此方法将 label 覆盖为 non_nodule。
        """
        self.db.query(Prediction).filter(Prediction.id == pred_id).update(
            {"label": new_label})
        self.db.commit()

    def get_by_slice(self, slice_id: int) -> list:
        return self.db.query(Prediction).filter(
            Prediction.slice_id == slice_id).order_by(Prediction.id.desc()).all()

    def count_in_range(self, date_from: Optional[str] = None, date_to: Optional[str] = None) -> int:
        q = self.db.query(Prediction)
        if date_from:
            q = q.filter(Prediction.created_at >= date_from)
        if date_to:
            q = q.filter(Prediction.created_at <= date_to + "T23:59:59")
        return q.count()

    def count_positive(self, date_from: Optional[str] = None, date_to: Optional[str] = None) -> int:
        q = self.db.query(Prediction).filter(Prediction.label == "nodule")
        if date_from:
            q = q.filter(Prediction.created_at >= date_from)
        if date_to:
            q = q.filter(Prediction.created_at <= date_to + "T23:59:59")
        return q.count()

    def daily_stats(self, date_from: Optional[str] = None, date_to: Optional[str] = None) -> list:
        """按日统计上传量和阳性率"""
        from sqlalchemy import func, Integer
        q = self.db.query(
            func.date(Prediction.created_at).label("date"),
            func.count().label("total"),
            func.sum(func.cast(Prediction.label == "nodule", Integer)).label("positive")
        )
        if date_from:
            q = q.filter(Prediction.created_at >= date_from)
        if date_to:
            q = q.filter(Prediction.created_at <= date_to + "T23:59:59")
        q = q.group_by(func.date(Prediction.created_at)).order_by(func.date(Prediction.created_at))
        return [{"date": str(r.date), "upload_count": r.total,
                 "positive_rate": round(r.positive / r.total, 4) if r.total else 0}
                for r in q.all()]
