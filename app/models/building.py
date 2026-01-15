from app import Column, Integer, String, DateTime
from app import func
from app import Base
from app import JSON, Float, Boolean

class BuildingEnergyTopKPI(Base):
    __tablename__ = "building_energy_top_kpi"

    id = Column(Integer, primary_key=True, index=True)

    # Card 1
    surplus_available_kwh = Column(Float, nullable=False)
    surplus_vs_daily_avg_percent = Column(Float, nullable=False)

    # Card 2
    currently_distributed_kwh = Column(Float, nullable=False)
    active_destinations = Column(Integer, nullable=False)

    # Card 3
    available_for_distribution_kwh = Column(Float, nullable=False)
    unused_percent = Column(Float, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())