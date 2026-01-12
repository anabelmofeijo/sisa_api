from app import APIRouter

router = APIRouter()


@router.get("/")
async def running():
    return {"message": "energy is running"} 