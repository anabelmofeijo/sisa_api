from app.models.alert import Alert
from app.schemas.alerts import AlertCreate, AlertResponse, AlertResolve
from app import SessionLocal, get_db, HTTPException, Depends
from sqlalchemy.orm import Session
from app.schemas.alerts import ElevatorWorkingAlert, ElevatorWorkingAlertResponse


class AlertCRUD:

    @staticmethod
    def create_alert(db: Session, alert: AlertCreate) -> AlertResponse:
        db_alert = Alert(
            title=alert.title,
            description=alert.description,
            level=alert.level,
            device_id=alert.device_id,
            measured_value=alert.measured_value,
            unit=alert.unit,
            detected_at=alert.detected_at,
            status=alert.status
        )
        db.add(db_alert)
        db.commit()
        db.refresh(db_alert)
        return AlertResponse.from_orm(db_alert)

    @staticmethod
    def get_alert(db: Session, alert_id: int) -> AlertResponse:
        db_alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not db_alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        return AlertResponse.from_orm(db_alert)

    @staticmethod
    def get_all_alerts(db: Session) -> list[AlertResponse]:
        alerts = db.query(Alert).all()
        return [AlertResponse.from_orm(alert) for alert in alerts]

    @staticmethod
    def resolve_alert(db: Session, alert_id: int, alert_resolve: AlertResolve) -> AlertResponse:
        db_alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not db_alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        db_alert.is_resolved = True
        db_alert.resolved_at = alert_resolve.resolved_at
        db.commit()
        db.refresh(db_alert)
        return AlertResponse.from_orm(db_alert)

    @staticmethod
    def delete_alert(db: Session, alert_id: int) -> None:
        db_alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not db_alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        db.delete(db_alert)
        db.commit()

    @staticmethod
    def report_elevator_working_status(db: Session, alert: ElevatorWorkingAlert) -> ElevatorWorkingAlertResponse:
        db_alert = Alert(
            elevator_id=alert.elevator_id,
            is_working=1 if alert.is_working else 0,
            reported_at=alert.reported_at
        )
        db.add(db_alert)
        db.commit()
        db.refresh(db_alert)
        return ElevatorWorkingAlertResponse(
            id=db_alert.id,
            elevator_id=alert.elevator_id,
            is_working=alert.is_working,
            reported_at=alert.reported_at,
            created_at=db_alert.created_at
        )