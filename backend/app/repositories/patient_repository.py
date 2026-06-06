"""患者与检查数据访问层"""

from typing import Optional, Tuple
from sqlalchemy.orm import Session

from app.models.patient import Patient
from app.models.study import Study


class PatientRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, patient_code: str, gender: str, age_range: Optional[str], created_by: Optional[int]) -> Patient:
        patient = Patient(
            patient_code=patient_code,
            gender=gender,
            age_range=age_range,
            created_by=created_by,
        )
        self.db.add(patient)
        self.db.commit()
        self.db.refresh(patient)
        return patient

    def get_by_id(self, patient_id: int) -> Optional[Patient]:
        return self.db.query(Patient).filter(Patient.id == patient_id).first()

    def get_by_code(self, patient_code: str) -> Optional[Patient]:
        return self.db.query(Patient).filter(Patient.patient_code == patient_code).first()

    def is_code_taken(self, patient_code: str, exclude_id: Optional[int] = None) -> bool:
        q = self.db.query(Patient).filter(Patient.patient_code == patient_code)
        if exclude_id is not None:
            q = q.filter(Patient.id != exclude_id)
        return q.first() is not None

    def list_patients(
        self, patient_code: Optional[str] = None, gender: Optional[str] = None,
        page: int = 1, page_size: int = 20,
    ) -> Tuple[list, int]:
        q = self.db.query(Patient)
        if patient_code:
            q = q.filter(Patient.patient_code.like(f"%{patient_code}%"))
        if gender:
            q = q.filter(Patient.gender == gender)
        total = q.count()
        items = q.order_by(Patient.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
        return items, total


class StudyRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, patient_id: int, description: Optional[str], created_by: int) -> Study:
        study = Study(
            patient_id=patient_id,
            description=description,
            created_by=created_by,
        )
        self.db.add(study)
        self.db.commit()
        self.db.refresh(study)
        return study

    def get_by_id(self, study_id: int) -> Optional[Study]:
        return self.db.query(Study).filter(Study.id == study_id).first()

    def list_by_patient(self, patient_id: int) -> list:
        return self.db.query(Study).filter(Study.patient_id == patient_id).order_by(Study.id.desc()).all()
