"""审计日志数据访问"""

from typing import Optional, Tuple
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.user import User


class AuditRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, action: str, target_type: Optional[str] = None,
               target_id: Optional[int] = None, detail: Optional[str] = None) -> AuditLog:
        log = AuditLog(user_id=user_id, action=action, target_type=target_type,
                        target_id=target_id, detail=detail)
        self.db.add(log)
        self.db.commit()
        return log

    def list_logs(self, user_id: Optional[int] = None, action: Optional[str] = None,
                  date_from: Optional[str] = None, date_to: Optional[str] = None,
                  page: int = 1, page_size: int = 20) -> Tuple[list, int]:
        q = self.db.query(AuditLog, User).join(User, AuditLog.user_id == User.id)
        if user_id:
            q = q.filter(AuditLog.user_id == user_id)
        if action:
            q = q.filter(AuditLog.action == action)
        if date_from:
            q = q.filter(AuditLog.created_at >= date_from)
        if date_to:
            q = q.filter(AuditLog.created_at <= date_to + "T23:59:59")
        total = q.count()
        items = q.order_by(AuditLog.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
        return items, total
