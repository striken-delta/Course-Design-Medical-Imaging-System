"""
统一响应格式
"""

from typing import Any, Optional
from .errors import ErrorCode, ERROR_MESSAGES


def success_response(
    data: Any = None,
    message: str = "success",
    request_id: Optional[str] = None,
) -> dict:
    """构建成功响应"""
    return {
        "code": ErrorCode.SUCCESS,
        "message": message,
        "data": data,
        "request_id": request_id,
    }


def error_response(
    code: ErrorCode,
    message: Optional[str] = None,
    data: Any = None,
    request_id: Optional[str] = None,
) -> dict:
    """构建错误响应"""
    return {
        "code": code,
        "message": message or ERROR_MESSAGES.get(code, "未知错误"),
        "data": data,
        "request_id": request_id,
    }


def paginated_response(
    items: list,
    page: int,
    page_size: int,
    total: int,
) -> dict:
    """构建分页响应"""
    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
    }
