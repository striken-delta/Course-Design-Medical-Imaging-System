"""
认证路由：注册、登录、获取当前用户
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.errors import ErrorCode
from app.core.response import success_response, error_response
from app.schemas.auth import LoginRequest, RegisterRequest, UserInfo
from app.services.auth_service import AuthService
from app.services.audit_service import AuditService
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/v1/auth", tags=["认证"])


@router.post("/register")
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    """
    患者自行注册

    - 仅允许注册 patient 角色
    - 密码长度 >= 6，需包含字母、数字、下划线中至少两种
    - 用户名全局唯一
    """
    service = AuthService(db)
    user, error = service.register(
        username=body.username,
        password=body.password,
        role="patient",  # 注册接口强制注册为 patient
        patient_code=body.patient_code,
    )

    if error:
        return error_response(error)

    AuditService(db).log(user.id, "register", "user", user.id, f"患者注册: {user.username}")

    user_info = {
        "id": user.id,
        "username": user.username,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat() if user.created_at else "",
    }
    return success_response(user_info, "注册成功")


@router.post("/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    """
    用户登录（所有角色通用）

    - 返回 JWT Token 和用户信息
    - 根据角色不同，前端跳转至对应的主页
    """
    service = AuthService(db)
    token, user_info, error = service.login(
        username=body.username,
        password=body.password,
    )

    if error:
        return error_response(error, "登录失败，请检查账号或密码")

    AuditService(db).log(user_info["id"], "login", "user", user_info["id"], f"用户登录: {user_info['username']}")

    return success_response({
        "access_token": token,
        "token_type": "bearer",
        "user": user_info,
    }, "登录成功")


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息"""
    return success_response({
        "id": current_user.id,
        "username": current_user.username,
        "role": current_user.role,
        "patient_id": current_user.patient_id,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else "",
    })
