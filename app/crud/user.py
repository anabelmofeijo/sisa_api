from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.core.security import hash_password


class CRUDUser:
    @staticmethod
    def create_user(db: Session, user: UserCreate) -> UserResponse:
        db_user = User(
            name=user.name,
            lastname=user.lastname,
            email=user.email,
            building=user.building,
            password=hash_password(user.password),
            phone=user.phone,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return UserResponse.from_orm(db_user)
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[UserResponse]:
        db_user = db.query(User).filter(User.email == email).first()
        if db_user:
            return db_user
        return None
    
    @staticmethod
    def get_user_by_password(db: Session, password: str) -> Optional[UserResponse]:
        db_user = db.query(User).filter(User.password == password).first()
        if db_user:
            return UserResponse.from_orm(db_user)
        return None
    
    @staticmethod
    def list_users(db: Session) -> list[UserResponse]:
        users = db.query(User).all()
        return [UserResponse.from_orm(user) for user in users]
    
    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        db_user = db.query(User).filter(User.id == user_id).first()
        if db_user:
            db.delete(db_user)
            db.commit()
            return True
        return False
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_update: UserCreate) -> Optional[UserResponse]:
        db_user = db.query(User).filter(User.id == user_id).first()
        if db_user:
            db_user.name = user_update.name
            db_user.lastname = user_update.lastname
            db_user.email = user_update.email
            db_user.building = user_update.building
            db_user.password = hash_password(user_update.password)
            db_user.phone = user_update.phone
            db.commit()
            db.refresh(db_user)
            return UserResponse.from_orm(db_user)
        return None
