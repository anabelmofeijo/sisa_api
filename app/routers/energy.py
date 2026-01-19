from app import APIRouter, Depends, get_db, HTTPException, SessionLocal
from app.schemas.energy import EnergyCreate, EnergyResponse
from app.crud.energy import EnergyCRUD


router = APIRouter()


@router.get("/")
async def running():
    return {"message": "energy is running"} 

@router.post("/create_energy", response_model=EnergyResponse)
def create_energy(energy: EnergyCreate, db=Depends(get_db)):
    crud = EnergyCRUD()
    return crud.create_energy(db, energy)   

@router.get("/get_energy/{energy_id}", response_model=EnergyResponse)
def get_energy(energy_id: int, db=Depends(get_db)):
    crud = EnergyCRUD()
    return crud.get_energy(db, energy_id)

@router.get("/list_energy", response_model=list[EnergyResponse])    
def list_energy(db=Depends(get_db)):
    crud = EnergyCRUD()
    return crud.get_all_energy(db)