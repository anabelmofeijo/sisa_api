from app import APIRouter, HTTPException, Depends, get_db
from sqlalchemy.orm import Session
from app.schemas.maintenance import (
    MaintenanceCreate,
    MaintenanceComplete
)
from app.crud.maintenance import CrudMaintenance

router = APIRouter()

@router.get("/components")
async def get_pending_components(db: Session = Depends(get_db)):
    """Retrieve maintenance tasks pending (ainda não concluídas)."""
    return CrudMaintenance.get_pending_maintenance(db)

@router.post("/components", status_code=201)
async def create_component(data: MaintenanceCreate, db: Session = Depends(get_db)):
    """
    Create a new component.

    This endpoint registers a new component that may require maintenance in the future.

    Args:
        data (MaintenanceCreate): Component information.
        db (Session): Database session dependency.

    Returns:
        dict: The created component information.
    """
    return CrudMaintenance.create_component(db, data)

@router.post("/components/{maintenance_id}/complete")
async def complete_maintenance(
    maintenance_id: int,
    data: MaintenanceComplete,
    db: Session = Depends(get_db)
):
    """Marca tarefa como concluída e atualiza `next_maintenance_date`."""
    return CrudMaintenance.complete_maintenance(db, maintenance_id, data)
