"""3D 视图相关 Pydantic 模型"""

from typing import Optional, List
from pydantic import BaseModel


class MarkerOut(BaseModel):
    id: int
    study_id: int
    slice_id: Optional[int] = None
    x: float
    y: float
    z: float
    confidence: float
    created_at: str

    model_config = {"from_attributes": True}


class View3DResponse(BaseModel):
    study_id: int
    model_url: str
    markers: List[MarkerOut]
