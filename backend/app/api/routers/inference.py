"""推理路由"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.errors import ErrorCode
from app.core.response import success_response, error_response
from app.services.inference_service import InferenceService
from app.services.audit_service import AuditService
from app.api.deps import require_doctor_or_admin
from app.models.user import User

router = APIRouter(prefix="/api/v1", tags=["推理"])


def _pred_to_dict(p) -> dict:
    return {"id": p.id, "slice_id": p.slice_id, "label": p.label,
            "confidence": p.confidence, "model_version": p.model_version,
            "inference_time_ms": p.inference_time_ms, "heatmap_path": p.heatmap_path,
            "created_at": p.created_at.isoformat() if p.created_at else ""}


@router.post("/inference/{slice_id}")
def run_inference(
    slice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor_or_admin),
):
    svc = InferenceService(db)
    pred, err = svc.run_inference(slice_id)
    if err:
        return error_response(err)
    AuditService(db).log(current_user.id, "inference", "prediction", pred.id, f"推理 Slice#{slice_id}: {pred.label} {pred.confidence}")
    return success_response(_pred_to_dict(pred), "推理完成")
