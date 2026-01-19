from app import APIRouter, HTTPException, Depends, get_db
from sqlalchemy.orm import Session
from app.schemas.maintenance import MaintenanceCreate, MaintenanceComplete, MaintenanceDashboardResponse, MaintenanceHistoryItem
from app.crud.maintenance import CrudMaintenance

router = APIRouter()

@router.get("/")
async def running():
    return {"message": "maintenance is running"}

@router.post("/create/")
def create_maintenance(maintenance: MaintenanceCreate, db: Session = Depends(get_db)):  
    return CrudMaintenance.create_maintenance(db, maintenance)

@router.post("/create_component/")
def create_component_maintenance(component_maintenance: MaintenanceCreate, db: Session = Depends(get_db)):  
    return CrudMaintenance.create_component_maintenance(db, component_maintenance)

@router.put("/complete/{maintenance_id}")
def complete_maintenance(maintenance_id: int, maintenance_complete: MaintenanceComplete, db: Session = Depends(get_db)):
    return CrudMaintenance.complete_maintenance(db, maintenance_id, maintenance_complete)

@router.get("/history/{component_id}", response_model=list[MaintenanceHistoryItem])
def get_maintenance_history(component_id: int,  db: Session = Depends(get_db)):
    return CrudMaintenance.get_maintenance_history(db, component_id)

@router.get("/all/",)
def get_all_maintenances(db: Session = Depends(get_db)):
    return CrudMaintenance.get_all_maintenances(db)

@router.get("/dashboard/", response_model=MaintenanceDashboardResponse)
def maintenance_dashboard(db: Session = Depends(get_db)):
    return CrudMaintenance.maintenance_dashboard(db)

@router.delete("/delete/{maintenance_id}")
def delete_maintenance(maintenance_id: int, db: Session = Depends(get_db)): 
    CrudMaintenance.delete_maintenance(db, maintenance_id)
    return {"message": "Maintenance record deleted successfully"}