"""
复核路由 — /api/v1/reviews

提供医生提交复核意见的 HTTP 接口。
仅医生和管理员可访问，复核操作会写入审计日志。

POST /api/v1/reviews
  - 请求体: CreateReviewRequest
  - 权限: doctor / admin
  - 副作用: 复核为 corrected 时会同步更新预测标签
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.errors import ErrorCode
from app.core.response import success_response, error_response
from app.schemas.review import CreateReviewRequest
from app.services.review_service import ReviewService
from app.services.audit_service import AuditService
from app.api.deps import require_doctor_or_admin
from app.models.user import User

router = APIRouter(prefix="/api/v1", tags=["复核"])


def _review_to_dict(r) -> dict:
    """将 Review ORM 对象转为字典，统一序列化"""
    return {"id": r.id, "prediction_id": r.prediction_id, "review_label": r.review_label,
            "corrected_label": r.corrected_label,
            "comment": r.comment, "reviewed_by": r.reviewed_by,
            "reviewed_at": r.reviewed_at.isoformat() if r.reviewed_at else ""}


@router.post("/reviews")
def submit_review(
    body: CreateReviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor_or_admin),
):
    """
    提交复核意见

    流程:
    1. 校验预测记录是否存在
    2. 若 corrected → 校验 corrected_label 必填 → 更新 predictions.label
    3. 创建 reviews 记录
    4. 记录审计日志
    """
    svc = ReviewService(db)
    # 调用业务层提交复核
    review, err = svc.submit(body.prediction_id, body.review_label, body.comment,
                            current_user.id, body.corrected_label)
    if err:
        return error_response(err)
    # 审计日志：记录谁在什么时间复核了哪条预测
    AuditService(db).log(current_user.id, "review", "prediction", body.prediction_id, f"复核: {body.review_label}")
    return success_response(_review_to_dict(review), "复核提交成功")
