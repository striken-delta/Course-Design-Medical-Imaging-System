"""
统一错误码定义

错误码约定:
- 0: 成功
- 1xxx: 客户端错误（参数、认证、权限、资源）
- 2xxx: 文件相关错误
- 3xxx: 推理相关错误
- 4xxx: 数据库错误
- 5xxx: 未知错误
"""

from enum import IntEnum


class ErrorCode(IntEnum):
    # 成功
    SUCCESS = 0

    # 参数错误 1xxx
    PARAM_ERROR = 1001
    UNAUTHORIZED = 1002
    FORBIDDEN = 1003
    NOT_FOUND = 1004
    CONFLICT = 1005

    # 密码安全错误
    PASSWORD_TOO_SHORT = 1006
    PASSWORD_WEAK = 1007

    # 注册相关错误
    REGISTRATION_FORBIDDEN = 1008

    # 文件错误 2xxx
    FILE_FORMAT_ERROR = 2001
    FILE_SIZE_EXCEEDED = 2002

    # 推理错误 3xxx
    INFERENCE_FAILED = 3001
    HEATMAP_FAILED = 3002

    # 数据库错误 4xxx
    DATABASE_ERROR = 4001

    # 未知错误 5xxx
    UNKNOWN_ERROR = 5001


# HTTP 状态码映射
ERROR_HTTP_STATUS = {
    ErrorCode.SUCCESS: 200,
    ErrorCode.PARAM_ERROR: 400,
    ErrorCode.UNAUTHORIZED: 401,
    ErrorCode.FORBIDDEN: 403,
    ErrorCode.NOT_FOUND: 404,
    ErrorCode.CONFLICT: 409,
    ErrorCode.PASSWORD_TOO_SHORT: 400,
    ErrorCode.PASSWORD_WEAK: 400,
    ErrorCode.REGISTRATION_FORBIDDEN: 403,
    ErrorCode.FILE_FORMAT_ERROR: 400,
    ErrorCode.FILE_SIZE_EXCEEDED: 400,
    ErrorCode.INFERENCE_FAILED: 500,
    ErrorCode.HEATMAP_FAILED: 500,
    ErrorCode.DATABASE_ERROR: 500,
    ErrorCode.UNKNOWN_ERROR: 500,
}

# 错误消息映射
ERROR_MESSAGES = {
    ErrorCode.SUCCESS: "success",
    ErrorCode.PARAM_ERROR: "参数错误",
    ErrorCode.UNAUTHORIZED: "请重新登录",
    ErrorCode.FORBIDDEN: "无权限访问该资源",
    ErrorCode.NOT_FOUND: "请求的资源不存在",
    ErrorCode.CONFLICT: "数据冲突，请检查后重试",
    ErrorCode.PASSWORD_TOO_SHORT: "密码长度不能小于6位",
    ErrorCode.PASSWORD_WEAK: "密码需包含字母、数字、下划线 _ 中至少两种字符",
    ErrorCode.REGISTRATION_FORBIDDEN: "医生和管理员账号不可自行注册，请联系管理员创建",
    ErrorCode.FILE_FORMAT_ERROR: "仅支持 png/jpg 格式",
    ErrorCode.FILE_SIZE_EXCEEDED: "文件大小超过限制",
    ErrorCode.INFERENCE_FAILED: "推理失败，请稍后重试",
    ErrorCode.HEATMAP_FAILED: "热力图生成失败",
    ErrorCode.DATABASE_ERROR: "数据库异常",
    ErrorCode.UNKNOWN_ERROR: "未知错误",
}
