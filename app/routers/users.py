from app import APIRouter
from app.schemas.user import UserCreate, UserResponse
from app.crud.user import CRUDUser


router = APIRouter()

@router.get("/")
async def running():
    return {"message": "users is running"}

@router.post("/create_user", response_model=UserResponse)
def create_user(user: UserCreate):
    create = CRUDUser.create_user()
    return create(user)
