from datetime import datetime

from app.models.alert import Alert
from app.schemas.alerts import (
    AlertCreate,
    AlertResponse,
    AlertResolve,
    ElevatorData,
    AlertLevel,
    ElevatorStatus,
    MotorStatus,
    BatteryTelemetry,
    ElevatorWorkingAlert,
    ElevatorWorkingAlertResponse,
)
from app import SessionLocal, get_db, HTTPException, Depends
from sqlalchemy.orm import Session


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
    def get_alerts_statistics(db: Session):
        """Get statistics about alerts by level and status."""
        from app.schemas.alerts import AlertsStatistics
        
        all_alerts = db.query(Alert).all()
        
        critical_count = len([a for a in all_alerts if a.level == AlertLevel.critical])
        warning_count = len([a for a in all_alerts if a.level == AlertLevel.warning])
        info_count = len([a for a in all_alerts if a.level == AlertLevel.info])
        resolved_count = len([a for a in all_alerts if a.status.value == "resolved"])
        total_count = len(all_alerts)
        
        return AlertsStatistics(
            critical=critical_count,
            warning=warning_count,
            info=info_count,
            resolved=resolved_count,
            total=total_count
        )

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
    def check_elevator_alerts(data: ElevatorData) -> list[AlertCreate]:
        alerts: list[AlertCreate] = []

        if data.battery_1 < 15 and data.battery_2 < 15:
            alerts.append(AlertCreate(
                title="Both batteries critically low",
                description="Both batteries are below 15%.",
                level=AlertLevel.critical,
                device_id=None,
                measured_value=min(data.battery_1, data.battery_2),
                unit="%",
            ))

        if data.elevator_status == ElevatorStatus.stopped and data.people_inside:
            alerts.append(AlertCreate(
                title="Elevator stopped with people inside",
                description="Elevator is stopped while passengers are inside.",
                level=AlertLevel.critical,
                device_id=None,
                measured_value=None,
                unit=None,
            ))

        if data.motor_status == MotorStatus.failure:
            alerts.append(AlertCreate(
                title="Motor failure",
                description="Motor status indicates failure.",
                level=AlertLevel.critical,
                device_id=None,
                measured_value=None,
                unit=None,
            ))

        if data.battery_1 < 40 or data.battery_2 < 40:
            alerts.append(AlertCreate(
                title="Low battery warning",
                description=f"One or more batteries below 40% (b1={data.battery_1}, b2={data.battery_2}).",
                level=AlertLevel.warning,
                device_id=None,
                measured_value=min(data.battery_1, data.battery_2),
                unit="%",
            ))

        if data.solar_generation == 0:
            alerts.append(AlertCreate(
                title="Solar generation lost",
                description="Solar generation is zero.",
                level=AlertLevel.warning,
                device_id=None,
                measured_value=0.0,
                unit="kW",
            ))

        if abs(data.battery_1 - data.battery_2) > 40:
            alerts.append(AlertCreate(
                title="Battery imbalance",
                description=f"Battery imbalance greater than 40% (difference={abs(data.battery_1 - data.battery_2)}).",
                level=AlertLevel.warning,
                device_id=None,
                measured_value=abs(data.battery_1 - data.battery_2),
                unit="%",
            ))

        if data.elevator_status == ElevatorStatus.moving and (data.battery_1 < 30 or data.battery_2 < 30):
            alerts.append(AlertCreate(
                title="Low battery while moving",
                description="Battery is below 30% while elevator is moving.",
                level=AlertLevel.warning,
                device_id=None,
                measured_value=min(data.battery_1, data.battery_2),
                unit="%",
            ))

        return alerts

    @staticmethod
    def check_battery_telemetry(telemetry: BatteryTelemetry) -> list[AlertCreate]:
        alerts: list[AlertCreate] = []

        if telemetry.voltage < 7.0:
            alerts.append(AlertCreate(
                title="Very low battery voltage",
                description=f"Battery voltage is below 7V ({telemetry.voltage:.2f}V).",
                level=AlertLevel.critical,
                device_id=telemetry.battery_id,
                measured_value=telemetry.voltage,
                unit="V",
                detected_at=datetime.utcnow(),
            ))

        if telemetry.percentage < 15.0:
            alerts.append(AlertCreate(
                title="Battery critically low",
                description=f"Battery percentage critically low ({telemetry.percentage:.1f}%).",
                level=AlertLevel.critical,
                device_id=telemetry.battery_id,
                measured_value=telemetry.percentage,
                unit="%",
                detected_at=datetime.utcnow(),
            ))

        if telemetry.percentage < 40.0 and telemetry.percentage >= 15.0:
            alerts.append(AlertCreate(
                title="Battery low warning",
                description=f"Battery percentage low ({telemetry.percentage:.1f}%).",
                level=AlertLevel.warning,
                device_id=telemetry.battery_id,
                measured_value=telemetry.percentage,
                unit="%",
                detected_at=datetime.utcnow(),
            ))

        if telemetry.random_discharge:
            alerts.append(AlertCreate(
                title="Random discharge event",
                description="Detected random unexpected discharge event on battery.",
                level=AlertLevel.info,
                device_id=telemetry.battery_id,
                measured_value=telemetry.percentage,
                unit="%",
                detected_at=datetime.utcnow(),
            ))

        if telemetry.swapped:
            alerts.append(AlertCreate(
                title="Battery swapped",
                description="Battery has been swapped successfully.",
                level=AlertLevel.info,
                device_id=telemetry.battery_id,
                measured_value=telemetry.percentage,
                unit="%",
                detected_at=datetime.utcnow(),
            ))

        return alerts

    @staticmethod
    def process_battery_telemetry(db: Session, telemetry: BatteryTelemetry) -> list[AlertResponse]:
        created_alerts: list[AlertResponse] = []
        for alert_payload in AlertCRUD.check_battery_telemetry(telemetry):
            created_alerts.append(AlertCRUD.create_alert(db, alert_payload))

        return created_alerts

    @staticmethod
    def process_elevator_data(db: Session, data: ElevatorData) -> list[AlertResponse]:
        created_alerts: list[AlertResponse] = []
        for alert_payload in AlertCRUD.check_elevator_alerts(data):
            # add detected timestamp automatically
            alert_payload_dict = alert_payload.dict()
            alert_payload_dict["detected_at"] = datetime.utcnow()
            alert_payload_with_date = AlertCreate(**alert_payload_dict)
            created_alerts.append(AlertCRUD.create_alert(db, alert_payload_with_date))

        return created_alerts

    @staticmethod
    def get_elevator_working_alerts(db: Session) -> list[ElevatorWorkingAlertResponse]:
        alerts = db.query(Alert).filter(Alert.elevator_id != None).all()
        return [ElevatorWorkingAlertResponse(
            id=a.id,
            elevator_id=a.elevator_id,
            is_working=bool(a.is_working),
            reported_at=a.reported_at,
            created_at=a.created_at
        ) for a in alerts]

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