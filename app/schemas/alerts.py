from app import BaseModel, datetime, Optional
from enum import Enum


class AlertLevel(str, Enum):
    critical = "critical"
    warning = "warning"
    info = "info"
    medium = "medium"
    low = "low"


class AlertStatus(str, Enum):
    active = "active"
    resolved = "resolved"


class ElevatorStatus(str, Enum):
    moving = "moving"
    stopped = "stopped"


class MotorStatus(str, Enum):
    ok = "ok"
    failure = "failure"


class ElevatorData(BaseModel):
    battery_1: float
    battery_2: float
    elevator_status: ElevatorStatus
    people_inside: bool
    temperature: float
    solar_generation: float
    motor_status: MotorStatus


class AlertCreate(BaseModel):
    title: str
    description: str
    level: AlertLevel
    device_id: Optional[int]
    measured_value: Optional[float]
    unit: Optional[str]
    detected_at: Optional[datetime] = None
    status: AlertStatus = AlertStatus.active


class AlertResolve(BaseModel):
    id: Optional[int] = None
    status: AlertStatus


class AlertResponse(BaseModel):
    id: int
    title: str
    description: str
    level: AlertLevel
    status: AlertStatus
    device_id: Optional[int]
    measured_value: Optional[float]
    unit: Optional[str]
    detected_at: datetime
    resolved_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class BatteryTelemetry(BaseModel):
    battery_name: Optional[str] = None
    battery_id: Optional[int] = None
    percentage: float
    voltage: float
    current: Optional[float] = None
    status: Optional[str] = None
    swapped: Optional[bool] = False
    random_discharge: Optional[bool] = False


class AlertsStatistics(BaseModel):
    critical: int
    warning: int
    info: int
    resolved: int
    total: int


class ElevatorFloorStatus(BaseModel):
    floor: int
    is_moving: bool


class ElevatorFloorResponse(BaseModel):
    floor: int
    is_moving: bool
    last_updated: datetime

    class Config:
        from_attributes = True


class ElevatorWorkingAlert(BaseModel):
    elevator_id: int
    is_working: bool


class ElevatorWorkingAlertResponse(ElevatorWorkingAlert):
    id: int
    is_working: bool
    reported_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True