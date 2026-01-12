from app import APIRouter

router = APIRouter()

@router.get("/")
async def running():
    return {"message": "users is running"}