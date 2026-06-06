"""切片相关 Pydantic 模型"""

from typing import Optional
from pydantic import BaseModel, Field


class SliceFilter(BaseModel):
    study_id: Optional[int] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class SliceOut(BaseModel):
    id: int
    study_id: int
    slice_index: int
    file_path: str
    file_format: str
    file_size: int
    uploaded_at: str
    uploaded_by: Optional[int] = None

    model_config = {"from_attributes": True}
