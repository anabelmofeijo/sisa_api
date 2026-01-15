from typing import List
from app import BaseModel
from app import Enum, datetime, Optional


class MaintenanceStatus(str, Enum):
    optimal = "optimal"
    warning = "warning"
    critical = "critical"


class MaintenanceType(str, Enum):
    preventive = "preventive"
    corrective = "corrective"


class MaintenanceKPI(BaseModel):
    operating_hours: int
    total_trips: int
    last_maintenance_date: datetime
    next_maintenance_date: datetime

class ComponentMaintenance(BaseModel):
    id: int
    name: str
    operating_hours: int

    last_maintenance_date: datetime
    next_maintenance_date: datetime

    is_overdue: bool
    reliability_percent: float
    status: MaintenanceStatus

    class Config:
        from_attributes = True

class MaintenanceCreate(BaseModel):
    component_id: int
    maintenance_type: MaintenanceType
    scheduled_date: datetime
    notes: Optional[str] = None


class MaintenanceComplete(BaseModel):
    completed_at: datetime
    notes: Optional[str] = None

class MaintenanceHistoryItem(BaseModel):
    id: int
    component_id: int
    component_name: str
    maintenance_type: MaintenanceType
    scheduled_date: datetime
    completed_at: Optional[datetime]
    notes: Optional[str]

    class Config:
        from_attributes = True

class MaintenanceDashboardResponse(BaseModel):
    kpis: MaintenanceKPI
    components: List[ComponentMaintenance]
    history: List[MaintenanceHistoryItem]