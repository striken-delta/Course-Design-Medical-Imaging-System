"""患者端路由"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.errors import ErrorCode
from app.core.response import success_response, error_response
from app.services.patient_portal_service import PatientPortalService
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/v1/patient", tags=["患者端"])


@router.get("/reports")
def get_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "patient":
        return error_response(ErrorCode.FORBIDDEN)
    if not current_user.patient_id:
        return success_response([])  # 尚未关联患者记录，返回空列表
    svc = PatientPortalService(db)
    reports = svc.get_reports(current_user.patient_id)
    return success_response(reports)


@router.get("/reports/{prediction_id}")
def get_report_detail(
    prediction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "patient":
        return error_response(ErrorCode.FORBIDDEN)
    if not current_user.patient_id:
        return error_response(ErrorCode.NOT_FOUND)
    svc = PatientPortalService(db)
    detail = svc.get_report_detail(current_user.patient_id, prediction_id)
    if not detail:
        return error_response(ErrorCode.NOT_FOUND)
    return success_response(detail)


@router.get("/progress")
def get_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "patient":
        return error_response(ErrorCode.FORBIDDEN)
    if not current_user.patient_id:
        return success_response({"status": "unlinked", "status_label": "尚未关联患者档案",
                                 "description": "请联系医生关联您的患者档案", "studies": []})
    svc = PatientPortalService(db)
    progress = svc.get_progress(current_user.patient_id)
    return success_response(progress)
