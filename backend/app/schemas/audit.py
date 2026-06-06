"""审计日志 Pydantic 模型"""

from typing import Optional
from pydantic import BaseModel, Field


class AuditFilter(BaseModel):
    user_id: Optional[int] = None
    action: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
