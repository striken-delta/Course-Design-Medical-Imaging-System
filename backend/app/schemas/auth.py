"""认证相关 Pydantic 模型"""

from typing import Optional
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., min_length=4, max_length=32, description="用户名")
    password: str = Field(..., min_length=1, description="密码")


class RegisterRequest(BaseModel):
    """患者注册请求（仅限患者角色自行注册）"""
    username: str = Field(..., min_length=4, max_length=32, description="用户名")
    password: str = Field(..., min_length=6, description="密码（至少6位，需包含字母、数字、下划线中至少两种）")
    patient_code: Optional[str] = Field(None, max_length=64, description="患者编码（选填，若填写且匹配已有记录则绑定）")


class UserInfo(BaseModel):
    """用户信息（脱敏返回）"""
    id: int
    username: str
    role: str
    is_active: bool
    created_at: str

    model_config = {"from_attributes": True}


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str
    token_type: str = "bearer"
    user: UserInfo


class TokenPayload(BaseModel):
    """JWT Token 解析后的 payload"""
    sub: str
    username: str
    role: str
    exp: int
    iat: int
