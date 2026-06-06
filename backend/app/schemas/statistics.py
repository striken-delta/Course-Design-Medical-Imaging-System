"""统计相关 Pydantic 模型"""

from typing import Optional
from pydantic import BaseModel
from datetime import date


class StatisticsQuery(BaseModel):
    date_from: Optional[str] = None
    date_to: Optional[str] = None
