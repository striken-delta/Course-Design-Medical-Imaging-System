"""报告检索路由"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.core.errors import ErrorCode
from app.core.response import success_response, error_response, paginated_response
from app.services.report_service import ReportService
from app.api.deps import require_doctor_or_admin
from app.models.user import User

router = APIRouter(prefix="/api/v1", tags=["报告"])


@router.get("/reports")
def search_reports(
    patient_code: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    label: Optional[str] = Query(None, pattern="^(nodule|non_nodule)$"),
    review_status: Optional[str] = Query(None, pattern="^(unreviewed|reviewed)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor_or_admin),
):
    svc = ReportService(db)
    items, total = svc.search_reports(patient_code, date_from, date_to, label, review_status, page, page_size)
    return success_response(paginated_response(items, page, page_size, total))


@router.get("/reports/{prediction_id}")
def get_report_detail(
    prediction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor_or_admin),
):
    svc = ReportService(db)
    detail = svc.get_report_detail(prediction_id)
    if not detail:
        return error_response(ErrorCode.NOT_FOUND)
    return success_response(detail)
