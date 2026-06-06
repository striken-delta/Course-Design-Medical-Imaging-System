"""预测相关 Pydantic 模型"""

from typing import Optional
from pydantic import BaseModel


class PredictionOut(BaseModel):
    id: int
    slice_id: int
    label: str
    confidence: float
    model_version: str
    inference_time_ms: int
    heatmap_path: Optional[str] = None
    created_at: str

    model_config = {"from_attributes": True}
