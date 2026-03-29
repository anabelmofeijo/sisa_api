import asyncio

from app import APIRouter, Depends, get_db, HTTPException, SessionLocal
from app.schemas.energy import EnergyCreate, EnergyResponse
from app.crud.energy import EnergyCRUD

router = APIRouter()
_energy_task = None

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

@router.get("/ist_energy", response_model=list[EnergyResponse])
async def ist_energy(db=Depends(get_db)):
    """
    Compatibility endpoint used by the frontend.

    It returns the list of energy snapshots and guarantees a recent
    snapshot calculated from the latest battery data.
    """
    crud = EnergyCRUD()
    return crud.get_all_energy(db)


async def _automatic_energy_snapshot():
    """Persist energy snapshots from battery telemetry every minute."""
    while True:
        with SessionLocal() as db:
            try:
                EnergyCRUD.ensure_recent_energy_snapshot(db)
            except Exception as exc:
                print(f"[ENERGY MONITOR] Failed to persist energy snapshot: {exc}")
        await asyncio.sleep(60)


def start_energy_monitor():
    """Start background energy snapshot generation."""
    global _energy_task
    if _energy_task is None or _energy_task.done():
        _energy_task = asyncio.create_task(_automatic_energy_snapshot())
        print("[ENERGY MONITOR] Started automatic energy snapshots (every 1 minute)")


async def stop_energy_monitor():
    """Stop background energy snapshot generation."""
    global _energy_task
    if _energy_task is not None:
        _energy_task.cancel()
        try:
            await _energy_task
        except asyncio.CancelledError:
            pass
        _energy_task = None
        print("[ENERGY MONITOR] Stopped automatic energy snapshots")
