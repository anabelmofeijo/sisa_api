from app import APIRouter, HTTPException, Depends, get_db
from sqlalchemy.orm import Session
from app.schemas.alerts import AlertCreate, AlertResponse, AlertResolve
from app.crud.alert import AlertCRUD


router = APIRouter()

@router.get("/")
async def running():
    return {"message": "alerts is running"}

@router.post("/create/", response_model=AlertResponse)
def create_alert(alert: AlertCreate, db: Session = Depends(get_db)):
    return AlertCRUD.create_alert(db, alert)

@router.get("/get_alert_by_id/{alert_id}", response_model=AlertResponse)
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    return AlertCRUD.get_alert(db, alert_id)

@router.get("/get_all_alerts/", response_model=list[AlertResponse])
def get_all_alerts(db: Session = Depends(get_db)):
    return AlertCRUD.get_all_alerts(db)

@router.put("/resolve/{alert_id}", response_model=AlertResponse)
def resolve_alert(alert_id: int, alert_resolve: AlertResolve, db: Session = Depends(get_db)):
    return AlertCRUD.resolve_alert(db, alert_id, alert_resolve)

@router.delete("/delete_alert/{alert_id}")
def delete_alert(alert_id: int, db: Session = Depends(get_db)): 
    AlertCRUD.delete_alert(db, alert_id)
    return {"message": "Alert deleted successfully"}
