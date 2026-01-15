from app import BaseModel


class BuildingEnergyTopKPI(BaseModel):
    id: int
    # Card 1 
    surplus_available_kwh: float
    surplus_vs_daily_avg_percent: float
    # Card 2
    currently_distributed_kwh: float
    active_destinations: int
    # Card 3
    available_for_distribution_kwh: float
    unused_percent: float

class BuildingEnergyDashboardResponse(BaseModel):
    id: int

    urplus_available_kwh: float
    surplus_vs_daily_avg_percent: float

    currently_distributed_kwh: float
    active_destinations: int

    available_for_distribution_kwh: float
    unused_percent: float

    class config:
        orm_mode = True