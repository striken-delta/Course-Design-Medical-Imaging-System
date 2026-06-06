"""用户管理相关 Pydantic 模型"""

from typing import Optional
from pydantic import BaseModel, Field


class CreateUserRequest(BaseModel):
    """管理员创建用户请求"""
    username: str = Field(..., min_length=4, max_length=32, description="用户名")
    password: str = Field(..., min_length=6, description="密码（至少6位，需包含字母、数字、下划线中至少两种）")
    role: str = Field(..., pattern="^(doctor|admin|patient)$", description="角色：doctor/admin/patient")
    patient_id: Optional[int] = Field(None, description="关联患者ID（role=patient时填写）")


class UpdateUserRequest(BaseModel):
    """修改用户请求"""
    role: Optional[str] = Field(None, pattern="^(doctor|admin|patient)$", description="新角色")
    is_active: Optional[bool] = Field(None, description="启用/禁用")


class UserOut(BaseModel):
    """用户输出"""
    id: int
    username: str
    role: str
    patient_id: Optional[int] = None
    is_active: bool
    created_at: str

    model_config = {"from_attributes": True}


class UserListFilter(BaseModel):
    """用户列表筛选参数"""
    role: Optional[str] = Field(None, pattern="^(doctor|admin|patient)$")
    keyword: Optional[str] = Field(None, max_length=64)
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
