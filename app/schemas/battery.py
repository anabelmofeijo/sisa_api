from app import BaseModel
from app import datetime, Optional


class BatteryCreate(BaseModel):
    battery_name: str
    status: bool
    percentage: float
    health: str
    temperature: float
    voltage: float
    current: float
    created_at: Optional[datetime] = None



class BatteryResponse(BaseModel):
    id: int 
    battery_name: str
    status: bool
    percentage: float
    health: str
    temperature: float
    voltage: float
    current: float
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True 
