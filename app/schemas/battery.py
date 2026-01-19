from app import BaseModel
from app import datetime, Optional
from app import Enum


class BateryType(str, Enum):
    first_batery = "Batery A"
    second_batery = "Batery B"

class Statustype(str, Enum):
    charging = "charging"
    discharging = "discharging"
    full = "full"
    not_charging = "not_charging"

class Healthtype(str, Enum):
    good = "good"
    overheat = "overheat"
    dead = "dead"
    unknown = "unknown"
    cold = "cold"
    over_voltage = "over_voltage"

class BatteryCreate(BaseModel):
    battery_name: BateryType
    status: Statustype
    percentage: float
    health: Healthtype
    temperature: float
    voltage: float
    current: float
    created_at: Optional[datetime] = None


class BatteryResponse(BaseModel):
    id: int 
    battery_name: BateryType
    status: Statustype
    percentage: float
    health: Healthtype
    temperature: float
    voltage: float
    current: float
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
