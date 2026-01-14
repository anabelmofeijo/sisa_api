from app import BaseModel, EmailStr
from app import datetime, Optional


class UserCreate(BaseModel):
    id: int
    name: str
    lastname: str
    email: EmailStr
    title: str
    password: str
    phone: Optional[str] = None
    created_at: Optional[datetime] = None


class UserResponse(BaseModel):
    id: int
    name: str
    lastname: str
    email: EmailStr
    title: str
    phone: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str