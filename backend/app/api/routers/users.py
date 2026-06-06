"""
用户管理路由：管理员 CRUD
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.core.errors import ErrorCode
from app.core.response import success_response, error_response, paginated_response
from app.schemas.user import CreateUserRequest, UpdateUserRequest
from app.services.user_service import UserService
from app.services.audit_service import AuditService
from app.api.deps import get_current_user, require_admin
from app.models.user import User

router = APIRouter(prefix="/api/v1/users", tags=["用户管理"])


def _user_to_dict(user: User) -> dict:
    """将 User ORM 对象转为前端需要的字典"""
    return {
        "id": user.id,
        "username": user.username,
        "role": user.role,
        "patient_id": user.patient_id,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat() if user.created_at else "",
    }


@router.get("")
def list_users(
    role: Optional[str] = Query(None, pattern="^(doctor|admin|patient)$"),
    keyword: Optional[str] = Query(None, max_length=64),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    管理员查询用户列表

    支持按角色、关键词筛选，支持分页
    """
    service = UserService(db)
    items, total = service.list_users(
        role=role,
        keyword=keyword,
        page=page,
        page_size=page_size,
    )

    return success_response(
        paginated_response(
            items=[_user_to_dict(u) for u in items],
            page=page,
            page_size=page_size,
            total=total,
        )
    )


@router.post("")
def create_user(
    body: CreateUserRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    管理员创建用户（支持创建 doctor / admin / patient）

    - 密码强度要求与注册一致
    - 用户名全局唯一
    """
    service = UserService(db)
    user, error = service.create_user(
        username=body.username,
        password=body.password,
        role=body.role,
        patient_id=body.patient_id,
    )

    if error:
        return error_response(error)

    AuditService(db).log(current_user.id, "create_user", "user", user.id, f"创建用户: {user.username}, 角色: {user.role}")
    return success_response(_user_to_dict(user), "用户创建成功")


@router.patch("/{user_id}")
def update_user(
    user_id: int,
    body: UpdateUserRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    管理员修改用户

    - 可修改角色或启用/禁用状态
    - 不支持修改密码（需单独的密码修改接口）
    """
    service = UserService(db)
    user, error = service.update_user(
        user_id=user_id,
        role=body.role,
        is_active=body.is_active,
    )

    if error:
        return error_response(error)

    AuditService(db).log(current_user.id, "modify_user", "user", user_id, f"修改用户: {body.role or ''} 启用:{body.is_active}")
    return success_response(_user_to_dict(user), "修改成功")
