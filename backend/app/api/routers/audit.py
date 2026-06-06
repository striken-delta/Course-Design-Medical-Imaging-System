"""审计日志路由"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.core.response import success_response, paginated_response
from app.services.audit_service import AuditService
from app.api.deps import require_admin
from app.models.user import User

router = APIRouter(prefix="/api/v1", tags=["审计"])


@router.get("/audit/logs")
def list_logs(
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    svc = AuditService(db)
    items, total = svc.list_logs(user_id, action, date_from, date_to, page, page_size)
    return success_response(paginated_response(items, page, page_size, total))
