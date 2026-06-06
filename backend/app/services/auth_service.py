"""认证服务：注册、登录、Token 签发"""

from typing import Optional, Tuple
from sqlalchemy.orm import Session

from app.repositories.user_repository import UserRepository
from app.repositories.patient_repository import PatientRepository
from app.core.security import (
    hash_password,
    verify_password,
    validate_password_strength,
    create_access_token,
)
from app.core.errors import ErrorCode
from app.core.permissions import can_register_role
from app.models.user import User


class AuthService:
    """认证与授权服务"""

    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)
        self.patient_repo = PatientRepository(db)

    def register(
        self,
        username: str,
        password: str,
        role: str = "patient",
        patient_code: Optional[str] = None,
    ) -> Tuple[Optional[User], Optional[ErrorCode]]:
        """
        患者注册

        规则:
        - patient 角色可自行注册（仅创建账号，不自动创建患者记录）
        - doctor / admin 角色不可自行注册
        - 密码须通过强度校验
        - 用户名须全局唯一
        - 若提供 patient_code 且匹配已有记录，则绑定（由医生告知编码后使用）
        - 患者记录由医生通过"新增患者"功能创建并关联账号

        返回 (User, None) 表示成功，(None, ErrorCode) 表示失败
        """
        # 1. 校验角色是否允许自行注册
        if not can_register_role(role):
            return None, ErrorCode.REGISTRATION_FORBIDDEN

        # 2. 校验密码强度
        error = validate_password_strength(password)
        if error:
            return None, error

        # 3. 校验用户名唯一性
        if self.user_repo.is_username_taken(username):
            return None, ErrorCode.CONFLICT

        # 4. 处理患者记录绑定（仅当患者提供了医生给的编码）
        patient_id: Optional[int] = None
        if patient_code:
            existing = self.patient_repo.get_by_code(patient_code)
            if existing:
                patient_id = existing.id
            else:
                return None, ErrorCode.NOT_FOUND  # 编码不存在

        # 5. 创建用户（patient_id 可能为 None，由医生后续绑定）
        password_hash = hash_password(password)
        user = self.user_repo.create(
            username=username,
            password_hash=password_hash,
            role=role,
            patient_id=patient_id,
        )
        return user, None

    def login(
        self,
        username: str,
        password: str,
    ) -> Tuple[Optional[str], Optional[dict], Optional[ErrorCode]]:
        """
        用户登录

        返回 (token, user_info, None) 表示成功
        返回 (None, None, ErrorCode) 表示失败
        """
        # 1. 查询用户
        user = self.user_repo.get_by_username(username)
        if not user:
            return None, None, ErrorCode.UNAUTHORIZED

        # 2. 检查账号是否启用
        if not user.is_active:
            return None, None, ErrorCode.UNAUTHORIZED

        # 3. 校验密码
        if not verify_password(password, user.password_hash):
            return None, None, ErrorCode.UNAUTHORIZED

        # 4. 签发 Token
        token = create_access_token(
            user_id=user.id,
            username=user.username,
            role=user.role,
        )

        # 5. 构建用户信息
        user_info = {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else "",
        }

        return token, user_info, None

    def get_current_user(self, token_payload: dict) -> Optional[User]:
        """根据 Token payload 获取当前用户"""
        user_id = int(token_payload.get("sub", 0))
        return self.user_repo.get_by_id(user_id)
