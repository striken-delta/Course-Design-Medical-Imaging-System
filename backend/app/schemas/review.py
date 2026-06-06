"""
复核相关 Pydantic 模型 — 请求体校验与响应序列化

CreateReviewRequest: 提交复核时的请求体
  - review_label=confirmed 时直接确认 AI 结果
  - review_label=corrected 时必须附带 corrected_label，告知纠正后的正确标签

ReviewOut: 复核记录响应，用于列表/详情展示
"""

from typing import Optional
from pydantic import BaseModel, Field, model_validator


class CreateReviewRequest(BaseModel):
    """提交复核请求体"""

    # 预测记录 ID
    prediction_id: int = Field(..., ge=1)
    # 复核结论：confirmed（确认 AI 结果）/ corrected（纠正 AI 结果）
    review_label: str = Field(..., pattern="^(confirmed|corrected)$")
    # 纠正后的标签，仅 corrected 时必填，取值 nodule / non_nodule
    corrected_label: Optional[str] = Field(None, pattern="^(nodule|non_nodule)$")
    # 复核评语（选填）
    comment: Optional[str] = Field(None, max_length=500)

    @model_validator(mode="after")
    def validate_corrected_label(self):
        """复核为 corrected 时，强制要求提供纠正后的标签"""
        if self.review_label == "corrected" and not self.corrected_label:
            raise ValueError("复核为 corrected 时，corrected_label 为必填项")
        return self


class ReviewOut(BaseModel):
    """复核记录响应"""

    id: int
    prediction_id: int
    review_label: str
    # 纠正后的标签（仅 corrected 时有值）
    corrected_label: Optional[str] = None
    comment: Optional[str] = None
    reviewed_by: int
    reviewed_by_name: Optional[str] = None
    reviewed_at: str

    model_config = {"from_attributes": True}
