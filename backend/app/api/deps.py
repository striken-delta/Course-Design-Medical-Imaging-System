"""
FastAPI 依赖项：获取当前用户、角色校验、数据库会话
"""

from typing import Optional
from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import decode_access_token
from app.core.errors import ErrorCode, ERROR_MESSAGES
from app.core.response import error_response
from app.models.user import User


def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> User:
    """
    从请求头 Authorization 中解析 JWT Token 并获取当前用户

    认证失败抛出 HTTP 401
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail=error_response(ErrorCode.UNAUTHORIZED, "请重新登录"),
        )

    # 解析 Bearer Token
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail=error_response(ErrorCode.UNAUTHORIZED, "请重新登录"),
        )

    token = parts[1]
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=401,
            detail=error_response(ErrorCode.UNAUTHORIZED, "登录已过期，请重新登录"),
        )

    user_id = int(payload.get("sub", 0))
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=401,
            detail=error_response(ErrorCode.UNAUTHORIZED, "用户不存在"),
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail=error_response(ErrorCode.FORBIDDEN, "账号已被禁用"),
        )

    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """要求管理员角色"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail=error_response(ErrorCode.FORBIDDEN, "仅管理员可执行此操作"),
        )
    return current_user


def require_doctor_or_admin(current_user: User = Depends(get_current_user)) -> User:
    """要求医生或管理员角色"""
    if current_user.role not in ("doctor", "admin"):
        raise HTTPException(
            status_code=403,
            detail=error_response(ErrorCode.FORBIDDEN, "无权限访问"),
        )
    return current_user


def require_patient(current_user: User = Depends(get_current_user)) -> User:
    """要求患者角色"""
    if current_user.role != "patient":
        raise HTTPException(
            status_code=403,
            detail=error_response(ErrorCode.FORBIDDEN, "无权限访问"),
        )
    return current_user
