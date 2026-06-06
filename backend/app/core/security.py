"""
安全模块：密码哈希、密码强度校验、JWT 签发与解析
"""

import re
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from jose import JWTError, jwt

from .config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from .errors import ErrorCode


def _encode_password(password: str) -> bytes:
    """
    将密码编码为 bytes，处理 bcrypt 的 72 字节限制

    bcrypt 最多处理 72 字节的输入，超过会报错。
    对于极长密码，取前 72 字节（UTF-8 编码），这在安全性和兼容性之间取得平衡。
    """
    encoded = password.encode("utf-8")
    if len(encoded) > 72:
        encoded = encoded[:72]
    return encoded


def hash_password(password: str) -> str:
    """对密码进行 bcrypt 哈希，返回字符串"""
    pw_bytes = _encode_password(password)
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pw_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """校验明文密码与哈希值是否匹配"""
    pw_bytes = _encode_password(plain_password)
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(pw_bytes, hashed_bytes)


def validate_password_strength(password: str) -> Optional[ErrorCode]:
    """
    校验密码强度

    规则:
    1. 密码长度 >= 6
    2. 必须包含字母、数字、下划线 _ 中至少两种字符

    返回 None 表示校验通过，否则返回对应的 ErrorCode
    """
    # 规则1: 长度 >= 6
    if len(password) < 6:
        return ErrorCode.PASSWORD_TOO_SHORT

    # 规则2: 检查包含的字符类型数量
    categories = 0
    if re.search(r'[a-zA-Z]', password):  # 字母
        categories += 1
    if re.search(r'[0-9]', password):     # 数字
        categories += 1
    if '_' in password:                   # 下划线
        categories += 1

    if categories < 2:
        return ErrorCode.PASSWORD_WEAK

    return None


def create_access_token(user_id: int, username: str, role: str) -> str:
    """签发 JWT Token"""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "username": username,
        "role": role,
        "exp": int(expire.timestamp()),
        "iat": int(now.timestamp()),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """
    解析 JWT Token，返回 payload 字典

    返回 None 表示 Token 无效或过期
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
