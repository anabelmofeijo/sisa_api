from app import APIRouter
from app import HTTPException
from app.crud.battery import BatteryCRUD
from app.schemas.battery import BatteryCreate, BatteryResponse
from app import Depends
from sqlalchemy.orm import Session
from app import get_db

router = APIRouter()

@router.get("/")
async def running():
    return {"message": "batteries is running"}

@router.post("/create_battery", response_model=BatteryResponse)
def create_battery(battery: BatteryCreate, db: Session = Depends(get_db)):
    crud = BatteryCRUD()
    return crud.create_battery(db, battery)

@router.get("/list_batteries", response_model=list[BatteryResponse])
def list_batteries(db: Session = Depends(get_db)):
    crud = BatteryCRUD()
    return crud.get_all_batteries(db)

@router.get("/get_battery/{battery_id}", response_model=BatteryResponse)
def get_battery(battery_id: int, db: Session = Depends(get_db)):
    crud = BatteryCRUD()
    return crud.get_battery(db, battery_id) 

@router.get("/get_batteries_by_name/{battery_name}", response_model=list[BatteryResponse])
def get_batteries_by_name(battery_name: str, db: Session = Depends(get_db)):
    crud = BatteryCRUD()
    return crud.get_all_batteries_by_the_name(db, battery_name)