"""
权限控制模块：基于角色的访问控制（RBAC）
"""

from typing import Optional

from .errors import ErrorCode


# 角色定义
ROLE_DOCTOR = "doctor"
ROLE_ADMIN = "admin"
ROLE_PATIENT = "patient"

ALL_ROLES = {ROLE_DOCTOR, ROLE_ADMIN, ROLE_PATIENT}
DOCTOR_ADMIN_ROLES = {ROLE_DOCTOR, ROLE_ADMIN}
ADMIN_ONLY = {ROLE_ADMIN}
PATIENT_ONLY = {ROLE_PATIENT}


def check_role(user_role: str, allowed_roles: set[str]) -> Optional[ErrorCode]:
    """
    校验用户角色是否在允许的角色集合中

    返回 None 表示校验通过，否则返回 ErrorCode.FORBIDDEN
    """
    if user_role not in allowed_roles:
        return ErrorCode.FORBIDDEN
    return None


def can_register_role(target_role: str) -> bool:
    """
    判断目标角色是否允许通过注册接口自行注册

    - patient: 允许自行注册
    - doctor / admin: 不允许自行注册，只能由管理员创建
    """
    return target_role == ROLE_PATIENT


def is_admin(user_role: str) -> bool:
    """是否管理员角色"""
    return user_role == ROLE_ADMIN


def is_doctor(user_role: str) -> bool:
    """是否医生角色"""
    return user_role == ROLE_DOCTOR


def is_patient(user_role: str) -> bool:
    """是否患者角色"""
    return user_role == ROLE_PATIENT
