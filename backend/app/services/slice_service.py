"""切片业务服务"""

from typing import Optional, Tuple
from sqlalchemy.orm import Session

from app.repositories.slice_repository import SliceRepository
from app.repositories.patient_repository import StudyRepository
from app.storage.file_storage import validate_file, save_slice_file
from app.core.errors import ErrorCode
from app.models.ct_slice import CtSlice


class SliceService:
    def __init__(self, db: Session):
        self.slice_repo = SliceRepository(db)
        self.study_repo = StudyRepository(db)

    def upload(self, file_content: bytes, filename: str, file_size: int,
               study_id: int, slice_index: int, uploaded_by: int,
               ) -> Tuple[Optional[CtSlice], Optional[ErrorCode]]:
        # 校验文件
        ok, err = validate_file(filename, file_size)
        if not ok:
            return None, ErrorCode.FILE_FORMAT_ERROR if "格式" in err else ErrorCode.FILE_SIZE_EXCEEDED
        # 校验 study 存在
        study = self.study_repo.get_by_id(study_id)
        if not study:
            return None, ErrorCode.NOT_FOUND
        # 保存文件
        ext = filename.rsplit(".", 1)[-1].lower()
        file_path = save_slice_file(file_content, filename, study_id, slice_index)
        # 写数据库
        s = self.slice_repo.create(study_id, slice_index, file_path, ext, file_size, uploaded_by)
        return s, None

    def list_slices(self, study_id: Optional[int] = None, page: int = 1, page_size: int = 20
                    ) -> Tuple[list, int]:
        return self.slice_repo.list_slices(study_id, page, page_size)

    def get_slice(self, slice_id: int) -> Optional[CtSlice]:
        return self.slice_repo.get_by_id(slice_id)
