"""报告相关 Pydantic 模型"""

from typing import Optional
from pydantic import BaseModel, Field


class ReportFilter(BaseModel):
    patient_code: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    label: Optional[str] = Field(None, pattern="^(nodule|non_nodule)$")
    review_status: Optional[str] = Field(None, pattern="^(unreviewed|reviewed)$")
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
