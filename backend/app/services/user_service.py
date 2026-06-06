"""用户管理服务"""

from typing import Optional, Tuple
from sqlalchemy.orm import Session

from app.repositories.user_repository import UserRepository
from app.core.security import hash_password, validate_password_strength
from app.core.errors import ErrorCode
from app.models.user import User


class UserService:
    """用户管理服务（管理员专用）"""

    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)

    def create_user(
        self,
        username: str,
        password: str,
        role: str,
        patient_id: Optional[int] = None,
    ) -> Tuple[Optional[User], Optional[ErrorCode]]:
        """
        管理员创建用户（支持创建任意角色）

        返回 (User, None) 表示成功，(None, ErrorCode) 表示失败
        """
        # 1. 校验密码强度
        error = validate_password_strength(password)
        if error:
            return None, error

        # 2. 校验用户名唯一性
        if self.user_repo.is_username_taken(username):
            return None, ErrorCode.CONFLICT

        # 3. 创建用户
        password_hash = hash_password(password)
        user = self.user_repo.create(
            username=username,
            password_hash=password_hash,
            role=role,
            patient_id=patient_id,
        )
        return user, None

    def update_user(
        self,
        user_id: int,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Tuple[Optional[User], Optional[ErrorCode]]:
        """管理员修改用户"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return None, ErrorCode.NOT_FOUND

        kwargs = {}
        if role is not None:
            kwargs["role"] = role
        if is_active is not None:
            kwargs["is_active"] = is_active

        if not kwargs:
            return user, None

        updated = self.user_repo.update(user, **kwargs)
        return updated, None

    def list_users(
        self,
        role: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[list, int]:
        """查询用户列表"""
        return self.user_repo.list_users(
            role=role,
            keyword=keyword,
            page=page,
            page_size=page_size,
        )
