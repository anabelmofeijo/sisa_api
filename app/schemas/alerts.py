from app import BaseModel, datetime, Optional
from enum import Enum


class AlertLevel(str, Enum):
    critical = "critical"
    medium = "medium"
    low = "low"


class AlertStatus(str, Enum):
    active = "active"
    resolved = "resolved"

class AlertCreate(BaseModel):
    title: str
    description: str 
    level: AlertLevel
    device_id: Optional[int] 
    measured_value: Optional[float] 
    unit: Optional[str] 
    status: AlertStatus = AlertStatus.active 

class AlertResolve(BaseModel):
    status: AlertStatus 
    resolved_at: Optional[datetime] 

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