"""统计业务服务"""

from typing import Optional
from sqlalchemy.orm import Session

from app.repositories.slice_repository import SliceRepository
from app.repositories.prediction_repository import PredictionRepository
from app.repositories.review_repository import ReviewRepository


class StatisticsService:
    def __init__(self, db: Session):
        self.slice_repo = SliceRepository(db)
        self.pred_repo = PredictionRepository(db)
        self.review_repo = ReviewRepository(db)

    def overview(self, date_from: Optional[str] = None, date_to: Optional[str] = None) -> dict:
        upload_count = self.slice_repo.count_in_range(date_from, date_to)
        inference_count = self.pred_repo.count_in_range(date_from, date_to)
        review_count = self.review_repo.count_in_range(date_from, date_to)

        positive_count = self.pred_repo.count_positive(date_from, date_to)
        positive_rate = round(positive_count / inference_count, 4) if inference_count else 0

        confirmed_count = self.review_repo.count_confirmed(date_from, date_to)
        consistency_rate = round(confirmed_count / review_count, 4) if review_count else 0

        # 获取最近30天的趋势（如无指定时间区间）
        trend = self.pred_repo.daily_stats(date_from, date_to)

        return {
            "overview": {
                "upload_count": upload_count,
                "inference_count": inference_count,
                "review_count": review_count,
                "positive_rate": positive_rate,
                "consistency_rate": consistency_rate,
            },
            "trend": trend,
        }
