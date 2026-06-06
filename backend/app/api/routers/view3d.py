"""3D 视图路由"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.errors import ErrorCode
from app.core.response import success_response, error_response
from app.services.view3d_service import View3DService
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/v1", tags=["3D视图"])


@router.get("/view3d/studies/{study_id}")
def get_3d_data(
    study_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    svc = View3DService(db)
    data = svc.get_data(study_id)
    if not data:
        return error_response(ErrorCode.NOT_FOUND)
    return success_response(data)
