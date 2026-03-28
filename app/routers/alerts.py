import asyncio
from datetime import datetime
from typing import Optional

from app import APIRouter, HTTPException, Depends, get_db
from sqlalchemy.orm import Session
from app.schemas.alerts import (
    AlertCreate,
    AlertResponse,
    AlertResolve,
    AlertsStatistics,
    ElevatorFloorStatus,
    ElevatorFloorResponse,
    BatteryTelemetry,
)
from app.schemas.battery import BateryType
from app.models.battery import Battery
from app.crud.alert import AlertCRUD
from app.core.config import SessionLocal

router = APIRouter()

last_floor_status: Optional[ElevatorFloorStatus] = None
last_battery_telemetry: Optional[BatteryTelemetry] = None
_monitor_task: Optional[asyncio.Task] = None



@router.post("/create", response_model=AlertResponse, name="alerts_create")
async def alerts_create(alert: AlertCreate, db: Session = Depends(get_db)):
    """Create a new alert."""
    return AlertCRUD.create_alert(db, alert)


@router.get("", response_model=list[AlertResponse], name="alerts_list")
async def alerts_list(db: Session = Depends(get_db)):
    """List all alerts."""
    return AlertCRUD.get_all_alerts(db)


@router.get("/statistics", response_model=AlertsStatistics, name="alerts_statistics")
async def alerts_statistics(db: Session = Depends(get_db)):
    """Get alerts statistics (critical, warning, info, resolved count)."""
    return AlertCRUD.get_alerts_statistics(db)


@router.put("/{alert_id}/resolve", response_model=AlertResponse, name="alerts_resolve")
async def alerts_resolve(alert_id: int, alert_resolve: AlertResolve, db: Session = Depends(get_db)):
    """Update alert as resolved."""
    return AlertCRUD.resolve_alert(db, alert_id, alert_resolve)


@router.delete("/{alert_id}", name="alerts_delete")
async def alerts_delete(alert_id: int, db: Session = Depends(get_db)):
    """Delete an alert."""
    AlertCRUD.delete_alert(db, alert_id)
    return {"id": alert_id, "message": "Alert deleted successfully"}


@router.post("/elevator-status", response_model=ElevatorFloorResponse, name="elevator_status_update")
async def elevator_status_update(status: ElevatorFloorStatus):
    """Send elevator floor and movement status."""
    global last_floor_status
    last_floor_status = status
    return ElevatorFloorResponse(
        floor=status.floor,
        is_moving=status.is_moving,
        last_updated=datetime.utcnow()
    )


@router.post("/battery-telemetry", response_model=AlertResponse, name="battery_telemetry_update")
async def battery_telemetry_update(telemetry: BatteryTelemetry, db: Session = Depends(get_db)):
    """Send battery telemetry data."""
    global last_battery_telemetry
    last_battery_telemetry = telemetry
    alerts = AlertCRUD.process_battery_telemetry(db, telemetry)
    if alerts:
        return alerts[0]
    return AlertResponse(
        id=0,
        title="Battery ok",
        description="No alerts detected",
        level="info",
        status="active",
        device_id=telemetry.battery_id,
        measured_value=telemetry.percentage,
        unit="%",
        detected_at=datetime.utcnow(),
        resolved_at=None,
        created_at=datetime.utcnow()
    )


@router.get("/elevator-status", response_model=Optional[ElevatorFloorResponse], name="elevator_status_get")
async def elevator_status_get():
    """Get current elevator floor and movement status."""
    if last_floor_status is None:
        raise HTTPException(status_code=404, detail="No elevator status data available")
    return ElevatorFloorResponse(
        floor=last_floor_status.floor,
        is_moving=last_floor_status.is_moving,
        last_updated=datetime.utcnow()
    )


async def _automatic_system_monitor():
    """Monitor battery data from database every 2 minutes and generate alerts."""
    
    while True:
        await asyncio.sleep(120)  # 2 minutes
        
        with SessionLocal() as db:
            try:
                # Get latest battery records from database
                batteries = db.query(Battery).order_by(Battery.created_at.desc()).limit(2).all()
                
                if not batteries:
                    print(f"[ALERT MONITOR] ⚠️ No battery data in database yet")
                    continue
                
                for battery in batteries:
                    print(f"[ALERT MONITOR] Checking {battery.battery_name.value} - Voltage: {battery.voltage}V, Percentage: {battery.percentage}%")
                    
                    # Convert Battery to BatteryTelemetry
                    telemetry = BatteryTelemetry(
                        battery_id=battery.id,
                        battery_name=battery.battery_name.value,
                        percentage=battery.percentage,
                        voltage=battery.voltage,
                        current=battery.current,
                        status=battery.status.value,
                        swapped=False,
                        random_discharge=False
                    )
                    
                    # Check for alerts
                    alerts = AlertCRUD.process_battery_telemetry(db, telemetry)
                    if alerts:
                        print(f"[ALERT MONITOR] ✅ Generated {len(alerts)} alert(s) for {battery.battery_name.value}")
                    else:
                        print(f"[ALERT MONITOR] ℹ️ {battery.battery_name.value} OK - No alerts")
                        
            except Exception as e:
                print(f"[ALERT MONITOR] ❌ Error monitoring database: {e}")


def start_alert_monitor():
    """Start the automatic alert monitoring system."""
    global _monitor_task
    if _monitor_task is None or _monitor_task.done():
        _monitor_task = asyncio.create_task(_automatic_system_monitor())
        print("[ALERT MONITOR] Started automatic monitoring (every 2 minutes)")


async def stop_alert_monitor():
    """Stop the automatic alert monitoring system."""
    global _monitor_task
    if _monitor_task is not None:
        _monitor_task.cancel()
        try:
            await _monitor_task
        except asyncio.CancelledError:
            pass
        _monitor_task = None
        print("[ALERT MONITOR] Stopped automatic monitoring")


def start_anomaly_monitor():
    start_alert_monitor()


async def stop_anomaly_monitor():
    await stop_alert_monitor()

