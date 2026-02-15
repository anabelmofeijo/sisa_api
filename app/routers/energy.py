from app import APIRouter, Depends, get_db, HTTPException, SessionLocal
from app.schemas.energy import EnergyCreate, EnergyResponse
from app.crud.energy import EnergyCRUD

router = APIRouter()

@router.get("/")
async def running():
    """
    Health check endpoint.

    Used to verify if the energy service is running correctly.

    Returns:
        dict: A confirmation message.
    """
    return {"message": "energy is running"} 

@router.post("/create_energy", response_model=EnergyResponse)
async def create_energy(energy: EnergyCreate, db=Depends(get_db)):
    """
    Create a new energy record.

    This endpoint registers energy-related data such as consumption,
    production, or measurements collected from sensors or systems.

    Args:
        energy (EnergyCreate): Energy data to be stored.
        db (Session): Database session dependency.

    Returns:
        EnergyResponse: The created energy record.
    """
    crud = EnergyCRUD()
    return crud.create_energy(db, energy)

@router.get("/get_energy/{energy_id}", response_model=EnergyResponse)
async def get_energy(energy_id: int, db=Depends(get_db)):
    """
    Retrieve energy data by ID.

    This endpoint fetches a specific energy record using its unique identifier.

    Args:
        energy_id (int): The ID of the energy record.
        db (Session): Database session dependency.

    Returns:
        EnergyResponse: The requested energy record.

    Raises:
        HTTPException: If the energy record is not found.
    """
    crud = EnergyCRUD()
    return crud.get_energy(db, energy_id)

@router.get("/list_energy", response_model=list[EnergyResponse])    
async def list_energy(db=Depends(get_db)):
    """
    Retrieve all energy records.

    This endpoint returns a list of all stored energy records,
    useful for analytics, dashboards, and reporting.

    Args:
        db (Session): Database session dependency.

    Returns:
        List[EnergyResponse]: A list of energy records.
    """
    crud = EnergyCRUD()
    return crud.get_all_energy(db)