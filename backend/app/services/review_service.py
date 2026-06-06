"""
复核业务服务 — ReviewService

核心逻辑:
1. 医生确认 AI 结果 (confirmed) → 仅记录复核，不修改预测
2. 医生纠正 AI 结果 (corrected) → 记录复核 + 同步更新预测标签为医生指定的值
   - 例如 AI 判为 nodule，医生纠正为 non_nodule → predictions.label 更新为 non_nodule
   - 例如 AI 判为 non_nodule，医生纠正为 nodule → predictions.label 更新为 nodule
"""

from typing import Optional, Tuple
from sqlalchemy.orm import Session

from app.repositories.review_repository import ReviewRepository
from app.repositories.prediction_repository import PredictionRepository
from app.core.errors import ErrorCode
from app.models.review import Review


class ReviewService:
    """复核业务：提交复核意见，必要时纠正 AI 预测标签"""

    def __init__(self, db: Session):
        self.review_repo = ReviewRepository(db)
        self.pred_repo = PredictionRepository(db)

    def submit(self, prediction_id: int, review_label: str, comment: Optional[str],
               reviewed_by: int, corrected_label: Optional[str] = None
               ) -> Tuple[Optional[Review], Optional[ErrorCode]]:
        """
        提交复核意见

        参数:
            prediction_id: AI 预测记录 ID
            review_label: 复核结论 (confirmed / corrected)
            comment: 复核评语（选填）
            reviewed_by: 复核医生 ID
            corrected_label: 纠正后的标签，仅 corrected 时必填 (nodule / non_nodule)

        返回:
            (Review, None) 成功
            (None, ErrorCode) 失败
        """
        # 校验预测记录存在
        prediction = self.pred_repo.get_by_id(prediction_id)
        if not prediction:
            return None, ErrorCode.NOT_FOUND

        # 复核与 AI 不一致时：先更新预测标签，再记录复核
        if review_label == "corrected":
            if not corrected_label:
                return None, ErrorCode.PARAM_ERROR
            # 将 prediction.label 更新为医生纠正后的值
            self.pred_repo.update_label(prediction_id, corrected_label)

        # 创建复核记录
        review = self.review_repo.create(
            prediction_id, review_label, comment, reviewed_by, corrected_label)
        return review, None
