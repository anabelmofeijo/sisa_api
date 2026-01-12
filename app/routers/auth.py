from app import APIRouter

router = APIRouter()

@router.get("/")
async def read_alerts():
    return {"message": "auth is running"}

