"""用户数据访问层"""

from typing import Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.user import User


class UserRepository:
    """用户数据仓库"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_username(self, username: str) -> Optional[User]:
        """按用户名查询用户"""
        return self.db.query(User).filter(User.username == username).first()

    def get_by_id(self, user_id: int) -> Optional[User]:
        """按 ID 查询用户"""
        return self.db.query(User).filter(User.id == user_id).first()

    def create(self, username: str, password_hash: str, role: str, patient_id: Optional[int] = None) -> User:
        """创建用户"""
        user = User(
            username=username,
            password_hash=password_hash,
            role=role,
            patient_id=patient_id,
            is_active=True,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user: User, **kwargs) -> User:
        """更新用户字段"""
        for key, value in kwargs.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        self.db.commit()
        self.db.refresh(user)
        return user

    def list_users(
        self,
        role: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[list[User], int]:
        """分页查询用户列表"""
        query = self.db.query(User)

        if role:
            query = query.filter(User.role == role)
        if keyword:
            query = query.filter(
                or_(
                    User.username.like(f"%{keyword}%"),
                )
            )

        total = query.count()
        items = query.order_by(User.id.desc()).offset((page - 1) * page_size).limit(page_size).all()

        return items, total

    def is_username_taken(self, username: str, exclude_id: Optional[int] = None) -> bool:
        """检查用户名是否已被占用"""
        query = self.db.query(User).filter(User.username == username)
        if exclude_id is not None:
            query = query.filter(User.id != exclude_id)
        return query.first() is not None
