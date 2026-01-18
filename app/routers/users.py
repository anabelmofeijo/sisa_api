from app import APIRouter, Depends, get_db, HTTPException
from app.schemas.user import UserCreate, UserResponse
from sqlalchemy.orm import Session
from app.crud.user import CRUDUser


router = APIRouter()

@router.get("/")
async def running():
    return {"message": "users is running"}

@router.post("/create_user", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    crud = CRUDUser()
    return crud.create_user(db, user)

@router.get("/list_users", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db)):
    crud = CRUDUser()
    return crud.list_users(db)  

@router.delete("/delete_user/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    crud = CRUDUser()
    success = crud.delete_user(db, user_id)
    if success:
        return {"message": "User deleted successfully"}
    return {"message": "User not found"}

@router.put("/update_user/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserCreate, db: Session = Depends(get_db)):
    crud = CRUDUser()
    updated_user = crud.update_user(db, user_id, user_update)
    if updated_user:
        return updated_user
    return {"message": "User not found"}

@router.get("/get_user_by_email_and_password", response_model=UserResponse)
def get_user_by_email_and_password(email: str, password: str, db: Session = Depends(get_db)):
    crud = CRUDUser()
    user = crud.get_user_by_email(db, email)
    if not user or user.password != password:
        raise HTTPException(status_code=404, detail="User not found")  # ✅ Correto
    return UserResponse.from_orm(user)