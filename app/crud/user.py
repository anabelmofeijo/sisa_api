from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse


class CRUDUser:

    def create_user(self, db: Session, user: UserCreate) -> UserResponse:
        db_user = User(
            name=user.name,
            lastname=user.lastname,
            email=user.email,
            title=user.title,
            password=user.password, 
            phone=user.phone,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return UserResponse.from_orm(db_user)
    
