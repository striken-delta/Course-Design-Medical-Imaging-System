"""患者与检查路由"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.core.errors import ErrorCode
from app.core.response import success_response, error_response, paginated_response
from app.schemas.patient import CreatePatientRequest, CreateStudyRequest
from app.services.patient_service import PatientService
from app.services.audit_service import AuditService
from app.api.deps import get_current_user, require_doctor_or_admin
from app.models.user import User

router = APIRouter(prefix="/api/v1", tags=["患者与检查"])


def _patient_to_dict(p) -> dict:
    return {
        "id": p.id, "patient_code": p.patient_code,
        "gender": p.gender, "age_range": p.age_range,
        "created_at": p.created_at.isoformat() if p.created_at else "",
        "created_by": p.created_by,
    }


def _study_to_dict(s) -> dict:
    return {
        "id": s.id, "patient_id": s.patient_id,
        "description": s.description,
        "created_at": s.created_at.isoformat() if s.created_at else "",
        "created_by": s.created_by,
    }


# ========== 患者 ==========

@router.get("/patients")
def list_patients(
    patient_code: Optional[str] = Query(None),
    gender: Optional[str] = Query(None, pattern="^(male|female|unknown)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor_or_admin),
):
    service = PatientService(db)
    items, total = service.list_patients(patient_code, gender, page, page_size)
    return success_response(paginated_response(
        [_patient_to_dict(p) for p in items], page, page_size, total))


@router.get("/patients/available-accounts")
def list_patient_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor_or_admin),
):
    """列出所有患者角色的用户账号（供医生创建患者时选择关联）"""
    from app.repositories.user_repository import UserRepository
    repo = UserRepository(db)
    items, _ = repo.list_users(role="patient", page=1, page_size=1000)
    result = []
    for u in items:
        result.append({
            "id": u.id,
            "username": u.username,
            "patient_id": u.patient_id,
            "linked": u.patient_id is not None,
        })
    return success_response(result)


@router.post("/patients")
def create_patient(
    body: CreatePatientRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor_or_admin),
):
    service = PatientService(db)
    patient, error = service.create_patient(
        body.patient_code, body.gender, body.age_range, current_user.id,
        user_id=body.user_id)
    if error:
        return error_response(error)
    AuditService(db).log(current_user.id, "create_patient", "patient", patient.id, f"创建患者: {patient.patient_code}")
    return success_response(_patient_to_dict(patient), "患者创建成功")


# ========== 检查 ==========

@router.get("/patients/{patient_id}/studies")
def list_studies(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor_or_admin),
):
    service = PatientService(db)
    studies = service.list_studies_by_patient(patient_id)
    return success_response([_study_to_dict(s) for s in studies])


@router.post("/patients/{patient_id}/studies")
def create_study(
    patient_id: int,
    body: CreateStudyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor_or_admin),
):
    service = PatientService(db)
    study, error = service.create_study(patient_id, body.description, current_user.id)
    if error:
        return error_response(error)
    AuditService(db).log(current_user.id, "create_study", "study", study.id, f"创建检查: Patient#{patient_id}")
    return success_response(_study_to_dict(study), "检查创建成功")


@router.get("/studies/{study_id}")
def get_study(
    study_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = PatientService(db)
    study = service.get_study(study_id)
    if not study:
        return error_response(ErrorCode.NOT_FOUND)
    return success_response(_study_to_dict(study))
