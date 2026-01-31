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
    """
    Health check endpoint.

    Used to verify if the battery service is running correctly.

    Returns:
        dict: A confirmation message.
    """
    return {"message": "batteries is running"}

@router.post("/create_battery", response_model=BatteryResponse)
def create_battery(battery: BatteryCreate, db: Session = Depends(get_db)):
    """
    Create a new battery.

    This endpoint registers a new battery in the system with its
    basic configuration and identification data.

    Args:
        battery (BatteryCreate): Battery data required for creation.
        db (Session): Database session dependency.

    Returns:
        BatteryResponse: The created battery.
    """
    crud = BatteryCRUD()
    return crud.create_battery(db, battery)

@router.get("/list_batteries", response_model=list[BatteryResponse])
def list_batteries(db: Session = Depends(get_db)):
    """
    Retrieve all batteries.

    This endpoint returns a list of all batteries registered in the system.

    Args:
        db (Session): Database session dependency.

    Returns:
        List[BatteryResponse]: A list of all batteries.
    """
    crud = BatteryCRUD()
    return crud.get_all_batteries(db)

@router.get("/get_battery/{battery_id}", response_model=BatteryResponse)
def get_battery(battery_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a battery by ID.

    This endpoint fetches detailed information about a battery
    using its unique identifier.

    Args:
        battery_id (int): The ID of the battery.
        db (Session): Database session dependency.

    Returns:
        BatteryResponse: The requested battery.

    Raises:
        HTTPException: If the battery is not found.
    """
    crud = BatteryCRUD()
    return crud.get_battery(db, battery_id)

@router.get("/get_batteries_by_name/{battery_name}", response_model=list[BatteryResponse])
def get_batteries_by_name(battery_name: str, db: Session = Depends(get_db)):
    """
    Retrieve batteries by name.

    This endpoint returns all batteries that match the given name.
    Useful when multiple batteries share the same identifier or label.

    Args:
        battery_name (str): Name of the battery.
        db (Session): Database session dependency.

    Returns:
        List[BatteryResponse]: Batteries matching the given name.
    """
    crud = BatteryCRUD()
    return crud.get_all_batteries_by_the_name(db, battery_name)
