"""统计路由"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.core.response import success_response
from app.services.statistics_service import StatisticsService
from app.api.deps import require_doctor_or_admin
from app.models.user import User

router = APIRouter(prefix="/api/v1", tags=["统计"])


@router.get("/statistics/overview")
def overview(
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor_or_admin),
):
    svc = StatisticsService(db)
    data = svc.overview(date_from, date_to)
    return success_response(data)


@router.get("/statistics/positive-rate")
def positive_rate(
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor_or_admin),
):
    svc = StatisticsService(db)
    data = svc.overview(date_from, date_to)
    return success_response({"trend": data["trend"]})


@router.get("/statistics/review-consistency")
def review_consistency(
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor_or_admin),
):
    svc = StatisticsService(db)
    data = svc.overview(date_from, date_to)
    return success_response({"consistency_rate": data["overview"]["consistency_rate"]})
