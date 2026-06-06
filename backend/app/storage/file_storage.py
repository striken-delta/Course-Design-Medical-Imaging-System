"""文件存储管理"""

import os
import shutil
import uuid
from pathlib import Path
from typing import Optional, Tuple

from app.core.config import UPLOAD_DIR, CT_SLICE_DIR, HEATMAP_DIR


ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def validate_file(filename: str, file_size: int) -> Tuple[bool, Optional[str]]:
    """校验文件格式和大小，返回 (是否通过, 错误消息)"""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"仅支持 {', '.join(ALLOWED_EXTENSIONS).upper()} 格式"
    if file_size > MAX_FILE_SIZE:
        return False, "文件大小不能超过 10MB"
    return True, None


def save_slice_file(file_content: bytes, original_filename: str, study_id: int, slice_index: int) -> str:
    """
    保存切片文件到磁盘

    目录结构: uploads/ct_slices/{study_id}/slice_{slice_index}_{uuid}.{ext}
    返回: 相对文件路径
    """
    ext = original_filename.rsplit(".", 1)[-1].lower()
    study_dir = CT_SLICE_DIR / str(study_id)
    study_dir.mkdir(parents=True, exist_ok=True)

    unique_id = uuid.uuid4().hex[:8]
    filename = f"slice_{slice_index}_{unique_id}.{ext}"
    filepath = study_dir / filename

    with open(filepath, "wb") as f:
        f.write(file_content)

    # 返回相对于 uploads 的路径
    return f"ct_slices/{study_id}/{filename}"


def get_slice_absolute_path(relative_path: str) -> Path:
    """获取切片文件的绝对路径"""
    return UPLOAD_DIR / relative_path


def save_heatmap(file_content: bytes, prediction_id: int) -> str:
    """保存热力图，返回相对路径"""
    heatmap_dir = HEATMAP_DIR / str(prediction_id)
    heatmap_dir.mkdir(parents=True, exist_ok=True)
    filepath = heatmap_dir / "cam.png"
    with open(filepath, "wb") as f:
        f.write(file_content)
    return f"heatmaps/{prediction_id}/cam.png"
