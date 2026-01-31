from app import APIRouter, HTTPException, Depends, get_db
from sqlalchemy.orm import Session
from app.schemas.building import BuildingEnergyTopKPICreate, BuildingEnergyDashboardResponse
from app.crud.building import BuildingCRUD as CrudBuilding

router = APIRouter()

@router.get("/")
async def running():
    """
    Health check endpoint.

    Used to verify if the building service is running correctly.

    Returns:
        dict: A confirmation message.
    """
    return {"message": "building is running"}

@router.get("/{building_id}/energy-dashboard")
def building_energy_dashboard(building_id: int, db: Session = Depends(get_db)):
    """
    Retrieve building energy dashboard.

    This endpoint returns the main energy performance indicators (Top KPIs)
    for a specific building, typically used to populate dashboards and reports.

    Args:
        building_id (int): The ID of the building.
        db (Session): Database session dependency.

    Returns:
        BuildingEnergyDashboardResponse: Energy KPIs and dashboard data.
    """
    return CrudBuilding.get_building_energy_top_kpi(db, building_id)

@router.post("/energy-top-kpi", status_code=201)
def create_building_energy_top_kpi(
    data: BuildingEnergyTopKPICreate,
    db: Session = Depends(get_db)
):
    """
    Create building energy Top KPI.

    This endpoint creates a new energy KPI entry for a building,
    such as consumption, efficiency, peak usage, or sustainability metrics.

    Args:
        data (BuildingEnergyTopKPICreate): Energy KPI data.
        db (Session): Database session dependency.

    Returns:
        BuildingEnergyTopKPICreate: The created KPI record.
    """
    return CrudBuilding.create_building_energy_top_kpi(db, data)

@router.put("/energy-top-kpi/{kpi_id}")
def update_building_energy_top_kpi(
    kpi_id: int,
    data: BuildingEnergyTopKPICreate,
    db: Session = Depends(get_db)
):
    """
    Update building energy Top KPI.

    This endpoint updates an existing energy KPI record
    identified by its unique KPI ID.

    Args:
        kpi_id (int): The ID of the KPI to update.
        data (BuildingEnergyTopKPICreate): Updated KPI data.
        db (Session): Database session dependency.

    Returns:
        BuildingEnergyTopKPICreate: The updated KPI record.
    """
    return CrudBuilding.update_building_energy_top_kpi(db, kpi_id, data)

@router.delete("/energy-top-kpi/{kpi_id}")
def delete_building_energy_top_kpi(
    kpi_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete building energy Top KPI.

    This endpoint permanently removes an energy KPI entry
    from the system using its KPI ID.

    Args:
        kpi_id (int): The ID of the KPI to delete.
        db (Session): Database session dependency.

    Returns:
        dict: Confirmation message.
    """
    CrudBuilding.delete_building(db, kpi_id)
    return {"message": "Building energy top KPI deleted successfully"}