from app import APIRouter, HTTPException, Depends, get_db
from sqlalchemy.orm import Session
from app.schemas.maintenance import MaintenanceCreate, MaintenanceComplete, MaintenanceDashboardResponse, MaintenanceHistoryItem
from app.crud.maintenance import CrudMaintenance

router = APIRouter()

@router.get("/")
async def running():
    return {"message": "maintenance is running"}

@router.get("/dashboard", response_model=MaintenanceDashboardResponse)
def maintenance_dashboard(db: Session = Depends(get_db)):
    return CrudMaintenance.maintenance_dashboard(db)

@router.get("/components")
def get_components(db: Session = Depends(get_db)):
    return CrudMaintenance.get_all_components(db)

@router.post("/components", status_code=201)
def create_component(data: MaintenanceCreate, db: Session = Depends(get_db)):
    return CrudMaintenance.create_component(db, data)


@router.post("/components/{maintenance_id}/complete")
def complete_maintenance(
    maintenance_id: int,
    data: MaintenanceComplete,
    db: Session = Depends(get_db)
):
    return CrudMaintenance.complete_maintenance(db, maintenance_id, data)

@router.get(
    "/components/{component_id}/history",
    response_model=list[MaintenanceHistoryItem]
)
def get_history(component_id: int, db: Session = Depends(get_db)):
    return CrudMaintenance.get_maintenance_history(db, component_id)

@router.delete("/components/{maintenance_id}")
def delete_component(maintenance_id: int, db: Session = Depends(get_db)):
    CrudMaintenance.delete_maintenance(db, maintenance_id)
    return {"message": "Componente removido com sucesso"}