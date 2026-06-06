"""患者与检查业务服务"""

from typing import Optional, Tuple
from sqlalchemy.orm import Session

from app.repositories.patient_repository import PatientRepository, StudyRepository
from app.core.errors import ErrorCode
from app.models.patient import Patient
from app.models.study import Study


class PatientService:
    def __init__(self, db: Session):
        self.patient_repo = PatientRepository(db)
        self.study_repo = StudyRepository(db)

    def create_patient(
        self, patient_code: str, gender: str, age_range: Optional[str], created_by: int,
        user_id: Optional[int] = None,
    ) -> Tuple[Optional[Patient], Optional[ErrorCode]]:
        if self.patient_repo.is_code_taken(patient_code):
            return None, ErrorCode.CONFLICT
        patient = self.patient_repo.create(patient_code, gender, age_range, created_by)
        # 若指定了关联账号，更新该用户的 patient_id
        if user_id:
            from app.repositories.user_repository import UserRepository
            user_repo = UserRepository(self.patient_repo.db)
            user = user_repo.get_by_id(user_id)
            if user:
                user_repo.update(user, patient_id=patient.id)
        return patient, None

    def list_patients(
        self, patient_code: Optional[str] = None, gender: Optional[str] = None,
        page: int = 1, page_size: int = 20,
    ) -> Tuple[list, int]:
        return self.patient_repo.list_patients(patient_code, gender, page, page_size)

    def create_study(
        self, patient_id: int, description: Optional[str], created_by: int,
    ) -> Tuple[Optional[Study], Optional[ErrorCode]]:
        patient = self.patient_repo.get_by_id(patient_id)
        if not patient:
            return None, ErrorCode.NOT_FOUND
        study = self.study_repo.create(patient_id, description, created_by)
        return study, None

    def get_study(self, study_id: int) -> Optional[Study]:
        return self.study_repo.get_by_id(study_id)

    def list_studies_by_patient(self, patient_id: int) -> list:
        return self.study_repo.list_by_patient(patient_id)
