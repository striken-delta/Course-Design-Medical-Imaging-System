"""审计日志业务服务"""

from typing import Optional, Tuple
from sqlalchemy.orm import Session

from app.repositories.audit_repository import AuditRepository


class AuditService:
    def __init__(self, db: Session):
        self.audit_repo = AuditRepository(db)

    def log(self, user_id: int, action: str, target_type: Optional[str] = None,
            target_id: Optional[int] = None, detail: Optional[str] = None):
        """写入审计日志（失败不影响主流程）"""
        try:
            self.audit_repo.create(user_id, action, target_type, target_id, detail)
        except Exception:
            pass  # 审计写入失败不应阻断主业务流程

    def list_logs(self, user_id: Optional[int] = None, action: Optional[str] = None,
                  date_from: Optional[str] = None, date_to: Optional[str] = None,
                  page: int = 1, page_size: int = 20) -> Tuple[list, int]:
        items, total = self.audit_repo.list_logs(user_id, action, date_from, date_to, page, page_size)
        logs = []
        for log, user in items:
            logs.append({
                "id": log.id, "user_id": log.user_id, "username": user.username,
                "action": log.action, "target_type": log.target_type,
                "target_id": log.target_id, "detail": log.detail,
                "created_at": log.created_at.isoformat() if log.created_at else "",
            })
        return logs, total
