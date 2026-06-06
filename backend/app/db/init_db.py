"""
数据库初始化：创建所有表并插入默认管理员账号
"""

from sqlalchemy.orm import Session

from app.db.session import engine, Base, SessionLocal
from app.models import User, Patient, Study, CtSlice, Prediction, Review, Lung3DMarker, AuditLog
from app.core.config import DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD
from app.core.security import hash_password, validate_password_strength


def create_tables():
    """创建所有数据库表"""
    Base.metadata.create_all(bind=engine)


def seed_default_admin(db: Session):
    """
    插入默认管理员账号

    如果默认管理员已存在则跳过
    """
    existing = db.query(User).filter(User.username == DEFAULT_ADMIN_USERNAME).first()
    if existing:
        return

    # 校验默认密码强度（安全兜底）
    error = validate_password_strength(DEFAULT_ADMIN_PASSWORD)
    if error:
        raise ValueError(f"默认管理员密码不符合安全要求: {error.name}")

    admin = User(
        username=DEFAULT_ADMIN_USERNAME,
        password_hash=hash_password(DEFAULT_ADMIN_PASSWORD),
        role="admin",
        is_active=True,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    print(f"[init_db] 默认管理员已创建: {admin.username} (role={admin.role})")


def init_database():
    """初始化数据库（创建表 + 种子数据）"""
    create_tables()
    db = SessionLocal()
    try:
        seed_default_admin(db)
    finally:
        db.close()
    print("[init_db] 数据库初始化完成")


if __name__ == "__main__":
    init_database()
