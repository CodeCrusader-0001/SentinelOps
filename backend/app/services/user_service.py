from typing import Optional, List
from sqlalchemy.orm import Session
from backend.app.models.user import User, UserRole
from backend.app.schemas.user import UserCreate
from backend.app.core.security import get_password_hash, verify_password

class UserService:
    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email.lower().strip()).first()

    @staticmethod
    def get_by_id(db: Session, user_id: str) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def create_user(db: Session, user_in: UserCreate) -> User:
        user = User(
            email=user_in.email.lower().strip(),
            hashed_password=get_password_hash(user_in.password),
            full_name=user_in.full_name,
            role=user_in.role,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        user = UserService.get_by_email(db, email)
        if not user or not user.is_active:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def seed_default_users(db: Session):
        """Seeds default Admin and IT Engineer accounts for seamless local evaluation."""
        if not UserService.get_by_email(db, "admin@sentinelops.io"):
            admin = User(
                email="admin@sentinelops.io",
                hashed_password=get_password_hash("Admin@Sentinel2026!"),
                full_name="Principal Security Admin",
                role=UserRole.ADMIN.value,
                is_active=True
            )
            db.add(admin)

        if not UserService.get_by_email(db, "engineer@sentinelops.io"):
            engineer = User(
                email="engineer@sentinelops.io",
                hashed_password=get_password_hash("Engineer@Sentinel2026!"),
                full_name="Lead IT Operations Engineer",
                role=UserRole.IT_ENGINEER.value,
                is_active=True
            )
            db.add(engineer)
            
        db.commit()
