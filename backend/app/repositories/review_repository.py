"""
复核数据访问层 — ReviewRepository

封装 reviews 表的 CRUD 与统计查询。
所有查询按 reviewed_at 降序排列，确保最新复核在前。
"""

from typing import Optional, Tuple
from sqlalchemy.orm import Session

from app.models.review import Review


class ReviewRepository:
    """复核数据访问"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, prediction_id: int, review_label: str, comment: Optional[str],
               reviewed_by: int, corrected_label: Optional[str] = None) -> Review:
        """
        创建一条复核记录

        参数:
            prediction_id: 预测记录 ID
            review_label: confirmed（确认）/ corrected（纠正）
            comment: 评语（选填）
            reviewed_by: 复核人 ID
            corrected_label: 纠正后标签（仅 corrected 时填写）
        """
        r = Review(prediction_id=prediction_id, review_label=review_label,
                    comment=comment, reviewed_by=reviewed_by,
                    corrected_label=corrected_label)
        self.db.add(r)
        self.db.commit()
        self.db.refresh(r)
        return r

    def get_by_prediction(self, prediction_id: int) -> list:
        """获取某条预测的全部复核历史（最新在前）"""
        return self.db.query(Review).filter(
            Review.prediction_id == prediction_id).order_by(Review.reviewed_at.desc()).all()

    def get_latest(self, prediction_id: int) -> Optional[Review]:
        """获取某条预测的最新一次复核"""
        return self.db.query(Review).filter(
            Review.prediction_id == prediction_id).order_by(Review.reviewed_at.desc()).first()

    def has_review(self, prediction_id: int) -> bool:
        """判断某条预测是否已被复核过"""
        return self.db.query(Review).filter(Review.prediction_id == prediction_id).first() is not None

    def count_in_range(self, date_from: Optional[str] = None, date_to: Optional[str] = None) -> int:
        """统计时间范围内的复核总数"""
        q = self.db.query(Review)
        if date_from:
            q = q.filter(Review.reviewed_at >= date_from)
        if date_to:
            q = q.filter(Review.reviewed_at <= date_to + "T23:59:59")
        return q.count()

    def count_confirmed(self, date_from: Optional[str] = None, date_to: Optional[str] = None) -> int:
        """统计时间范围内确认一致的复核数量（用于计算一致率）"""
        q = self.db.query(Review).filter(Review.review_label == "confirmed")
        if date_from:
            q = q.filter(Review.reviewed_at >= date_from)
        if date_to:
            q = q.filter(Review.reviewed_at <= date_to + "T23:59:59")
        return q.count()
