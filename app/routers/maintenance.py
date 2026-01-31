from app import APIRouter, HTTPException, Depends, get_db
from sqlalchemy.orm import Session
from app.schemas.maintenance import (
    MaintenanceCreate,
    MaintenanceComplete,
    MaintenanceDashboardResponse,
    MaintenanceHistoryItem
)
from app.crud.maintenance import CrudMaintenance

router = APIRouter()

@router.get("/")
async def running():
    """
    Health check endpoint.

    Used to verify if the maintenance service is running correctly.

    Returns:
        dict: A confirmation message.
    """
    return {"message": "maintenance is running"}

@router.get("/dashboard", response_model=MaintenanceDashboardResponse)
def maintenance_dashboard(db: Session = Depends(get_db)):
    """
    Retrieve maintenance dashboard.

    This endpoint returns an overview of maintenance activities,
    including pending, ongoing, and completed tasks.

    Args:
        db (Session): Database session dependency.

    Returns:
        MaintenanceDashboardResponse: Summary of maintenance activities.
    """
    return CrudMaintenance.maintenance_dashboard(db)

@router.get("/components")
def get_components(db: Session = Depends(get_db)):
    """
    Retrieve all components.

    This endpoint returns a list of all components that can have maintenance tasks.

    Args:
        db (Session): Database session dependency.

    Returns:
        List[dict]: List of components.
    """
    return CrudMaintenance.get_all_components(db)

@router.post("/components", status_code=201)
def create_component(data: MaintenanceCreate, db: Session = Depends(get_db)):
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
def complete_maintenance(
    maintenance_id: int,
    data: MaintenanceComplete,
    db: Session = Depends(get_db)
):
    """
    Mark a maintenance task as complete.

    This endpoint updates the status of a maintenance task to completed
    and allows adding completion notes or remarks.

    Args:
        maintenance_id (int): The ID of the maintenance task.
        data (MaintenanceComplete): Completion details (notes, timestamp, etc.).
        db (Session): Database session dependency.

    Returns:
        dict: The updated maintenance record.
    """
    return CrudMaintenance.complete_maintenance(db, maintenance_id, data)

@router.get(
    "/components/{component_id}/history",
    response_model=list[MaintenanceHistoryItem]
)
def get_history(component_id: int, db: Session = Depends(get_db)):
    """
    Retrieve maintenance history for a component.

    This endpoint returns all past maintenance tasks for a specific component.

    Args:
        component_id (int): The ID of the component.
        db (Session): Database session dependency.

    Returns:
        List[MaintenanceHistoryItem]: List of past maintenance records.
    """
    return CrudMaintenance.get_maintenance_history(db, component_id)

@router.delete("/components/{maintenance_id}")
def delete_component(maintenance_id: int, db: Session = Depends(get_db)):
    """
    Delete a maintenance task or component.

    This endpoint permanently removes a maintenance task or component
    from the system by its ID.

    Args:
        maintenance_id (int): The ID of the maintenance task to delete.
        db (Session): Database session dependency.

    Returns:
        dict: Confirmation message.
    """
    CrudMaintenance.delete_maintenance(db, maintenance_id)
    return {"message": "Component successfully removed"}