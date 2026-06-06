"""
复核模型 — Review

记录医生对 AI 预测结果的复核意见。
每条复核关联一条预测记录，包含复核结论（确认/纠正）和可选的纠正后标签。

复核结论:
- confirmed: 医生同意 AI 预测结果
- corrected: 医生不同意 AI 预测结果，需通过 corrected_label 给出正确标签
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.db.session import Base


class Review(Base):
    """医生复核记录"""

    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    # 关联的 AI 预测记录
    prediction_id = Column(Integer, ForeignKey("predictions.id"), nullable=False, index=True)
    # 复核结论: confirmed（与 AI 一致）/ corrected（纠正 AI 结果）
    review_label = Column(String(16), nullable=False)
    # 纠正后的标签，仅当 review_label == "corrected" 时有值
    corrected_label = Column(String(16), nullable=True)
    # 医生复核评语（选填，最长 500 字）
    comment = Column(String(500), nullable=True)
    # 执行复核的医生
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    # 复核时间
    reviewed_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Review(id={self.id}, label={self.review_label})>"
