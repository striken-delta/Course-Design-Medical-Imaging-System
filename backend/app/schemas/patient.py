"""患者与检查相关 Pydantic 模型"""

from typing import Optional
from pydantic import BaseModel, Field


class CreatePatientRequest(BaseModel):
    """新增患者请求"""
    patient_code: str = Field(..., min_length=1, max_length=64, description="脱敏患者编码")
    gender: str = Field("unknown", pattern="^(male|female|unknown)$", description="性别")
    age_range: Optional[str] = Field(None, max_length=16, description="年龄段，如 40-50")
    user_id: Optional[int] = Field(None, description="关联的患者账号ID（选填）")


class PatientOut(BaseModel):
    """患者输出"""
    id: int
    patient_code: str
    gender: str
    age_range: Optional[str] = None
    created_at: str
    created_by: Optional[int] = None

    model_config = {"from_attributes": True}


class PatientFilter(BaseModel):
    """患者检索筛选"""
    patient_code: Optional[str] = Field(None, max_length=64)
    gender: Optional[str] = Field(None, pattern="^(male|female|unknown)$")
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class CreateStudyRequest(BaseModel):
    """新增检查请求"""
    description: Optional[str] = Field(None, max_length=256, description="检查说明")


class StudyOut(BaseModel):
    """检查输出"""
    id: int
    patient_id: int
    description: Optional[str] = None
    created_at: str
    created_by: Optional[int] = None

    model_config = {"from_attributes": True}
