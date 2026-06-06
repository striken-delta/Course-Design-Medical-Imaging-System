"""切片路由"""

from fastapi import APIRouter, Depends, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.core.errors import ErrorCode
from app.core.response import success_response, error_response, paginated_response
from app.services.slice_service import SliceService
from app.services.audit_service import AuditService
from app.api.deps import get_current_user, require_doctor_or_admin
from app.models.user import User

router = APIRouter(prefix="/api/v1", tags=["切片"])


def _slice_to_dict(s) -> dict:
    fp = s.file_path
    if fp and not fp.startswith("/"):
        fp = "/uploads/" + fp
    return {"id": s.id, "study_id": s.study_id, "slice_index": s.slice_index,
            "file_path": fp, "file_format": s.file_format, "file_size": s.file_size,
            "uploaded_at": s.uploaded_at.isoformat() if s.uploaded_at else "",
            "uploaded_by": s.uploaded_by}


@router.post("/studies/{study_id}/slices")
async def upload_slice(
    study_id: int,
    file: UploadFile = File(...),
    slice_index: int = Form(0),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor_or_admin),
):
    svc = SliceService(db)
    content = await file.read()
    filename = file.filename or "unknown.png"
    s, err = svc.upload(content, filename, len(content), study_id, slice_index, current_user.id)
    if err:
        return error_response(err)
    AuditService(db).log(current_user.id, "upload", "slice", s.id, f"上传切片到 Study#{study_id}")
    return success_response(_slice_to_dict(s), "上传成功")


@router.get("/slices")
def list_slices(
    study_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor_or_admin),
):
    svc = SliceService(db)
    items, total = svc.list_slices(study_id, page, page_size)
    return success_response(paginated_response([_slice_to_dict(s) for s in items], page, page_size, total))


@router.get("/slices/{slice_id}")
def get_slice(
    slice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    svc = SliceService(db)
    s = svc.get_slice(slice_id)
    if not s:
        return error_response(ErrorCode.NOT_FOUND)
    return success_response(_slice_to_dict(s))
