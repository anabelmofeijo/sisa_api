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

    model_config = {
        "from_attributes": True
    }

class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    lastname: Optional[str] = None
    email: Optional[EmailStr] = None
    title: Optional[str] = None
    password: Optional[str] = None
    phone: Optional[str] = None
