from app import APIRouter, HTTPException, Depends, get_db
from sqlalchemy.orm import Session
from app.schemas.alerts import AlertCreate, AlertResponse, AlertResolve
from app.crud.alert import AlertCRUD
from app.schemas.alerts import ElevatorWorkingAlert, ElevatorWorkingAlertResponse

router = APIRouter()

@router.get("/")
async def running():
    """
    Health check endpoint.

    Used to verify if the alerts service is running correctly.

    Returns:
        dict: A confirmation message.
    """
    return {"message": "alerts is running"}

@router.post("/create/", response_model=AlertResponse)
async def create_alert(alert: AlertCreate, db: Session = Depends(get_db)):
    """
    Create a new alert.

    This endpoint registers a new alert in the system, such as incidents,
    warnings, or system-generated notifications.

    Args:
        alert (AlertCreate): Alert data to be created.
        db (Session): Database session dependency.

    Returns:
        AlertResponse: The created alert.
    """
    return AlertCRUD.create_alert(db, alert)

@router.get("/get_alert_by_id/{alert_id}", response_model=AlertResponse)
async def get_alert(alert_id: int, db: Session = Depends(get_db)):
    """
    Retrieve an alert by ID.

    This endpoint fetches a specific alert using its unique identifier.

    Args:
        alert_id (int): The ID of the alert.
        db (Session): Database session dependency.

    Returns:
        AlertResponse: The requested alert.

    Raises:
        HTTPException: If the alert does not exist.
    """
    return AlertCRUD.get_alert(db, alert_id)

@router.get("/get_all_alerts/", response_model=list[AlertResponse])
async def get_all_alerts(db: Session = Depends(get_db)):
    """
    Retrieve all alerts.

    This endpoint returns a list of all alerts registered in the system.

    Args:
        db (Session): Database session dependency.

    Returns:
        List[AlertResponse]: A list of all alerts.
    """
    return AlertCRUD.get_all_alerts(db)

@router.put("/resolve/{alert_id}", response_model=AlertResponse)
async def resolve_alert(alert_id: int, alert_resolve: AlertResolve, db: Session = Depends(get_db)):
    """
    Resolve an alert.

    This endpoint updates the status of an alert to resolved and may include
    resolution details such as comments or timestamps.

    Args:
        alert_id (int): The ID of the alert to resolve.
        alert_resolve (AlertResolve): Resolution information.
        db (Session): Database session dependency.

    Returns:
        AlertResponse: The resolved alert.
    """
    return AlertCRUD.resolve_alert(db, alert_id, alert_resolve)

@router.delete("/delete_alert/{alert_id}")
async def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    """
    Delete an alert by ID.

    This endpoint permanently removes an alert from the system.

    Args:
        alert_id (int): The ID of the alert to delete.
        db (Session): Database session dependency.

    Returns:
        dict: Confirmation message.
    """
    AlertCRUD.delete_alert(db, alert_id)
    return {"message": "Alert deleted successfully"}

@router.post("/report_elevator_working_status/", response_model=ElevatorWorkingAlertResponse)
async def report_elevator_working_status(alert: ElevatorWorkingAlert, db: Session = Depends(get_db)):
    """
    Report elevator working status.

    This endpoint is used to report whether an elevator is working or not.
    It creates a specialized alert related to elevator operational status.

    Args:
        alert (ElevatorWorkingAlert): Elevator status report data.
        db (Session): Database session dependency.

    Returns:
        ElevatorWorkingAlertResponse: The created elevator status alert.
    """
    return AlertCRUD.report_elevator_working_status(db, alert)

@router.get("/elevator_working_alerts/", response_model=list[ElevatorWorkingAlertResponse])
async def get_elevator_working_alerts(db: Session = Depends(get_db)):
    """
    Retrieve all elevator working status alerts.

    This endpoint returns a list of alerts related specifically
    to elevator operational conditions.

    Args:
        db (Session): Database session dependency.

    Returns:
        List[ElevatorWorkingAlertResponse]: Elevator working status alerts.
    """
    return AlertCRUD.get_elevator_working_alerts(db)
