from app import APIRouter, HTTPException, Depends, get_db
from sqlalchemy.orm import Session
from app.schemas.building import BuildingEnergyTopKPICreate, BuildingEnergyDashboardResponse
from app.crud.building import BuildingCRUD as CrudBuilding


router = APIRouter()

@router.get("/")
async def running():
    return {"message": "building is running"}

@router.get("/{building_id}/energy-dashboard")
def building_energy_dashboard(building_id: int, db: Session = Depends(get_db)):
    return CrudBuilding.get_building_energy_top_kpi(db, building_id)

@router.post("/energy-top-kpi", status_code=201)
def create_building_energy_top_kpi(
    data: BuildingEnergyTopKPICreate,
    db: Session = Depends(get_db)
):
    return CrudBuilding.create_building_energy_top_kpi(db, data)

@router.put("/energy-top-kpi/{kpi_id}")
def update_building_energy_top_kpi(
    kpi_id: int,
    data: BuildingEnergyTopKPICreate,
    db: Session = Depends(get_db)
):
    return CrudBuilding.update_building_energy_top_kpi(db, kpi_id, data)

@router.delete("/energy-top-kpi/{kpi_id}")
def delete_building_energy_top_kpi(kpi_id: int, db: Session = Depends   (get_db)):
    CrudBuilding.delete_building(db, kpi_id)
    return {"message": "Building energy top KPI deleted successfully"}