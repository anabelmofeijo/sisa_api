from app import HTTPException, Depends, get_db
from app.models.building import BuildingEnergyTopKPI as Building
from app.schemas.building import BuildingEnergyDashboardResponse, BuildingEnergyTopKPICreate
from sqlalchemy.orm import Session


class BuildingCRUD:

    @staticmethod
    def get_building_energy_top_kpi(db: Session, building_id: int) -> BuildingEnergyDashboardResponse:
        building = db.query(Building).filter(Building.id == building_id).first()
        if not building:
            raise HTTPException(status_code=404, detail="Building not found")
        return BuildingEnergyDashboardResponse.from_orm(building)
    
    @staticmethod
    def create_building_energy_top_kpi(db: Session, kpi_data: BuildingEnergyTopKPICreate) -> BuildingEnergyDashboardResponse:
        building = db.query(Building).filter(Building.id == kpi_data.id).first()
        if not building:
            raise HTTPException(status_code=404, detail="Building not found")
        
        building.surplus_available_kwh = kpi_data.surplus_available_kwh
        building.surplus_vs_daily_avg_percent = kpi_data.surplus_vs_daily_avg_percent
        building.currently_distributed_kwh = kpi_data.currently_distributed_kwh
        building.active_destinations = kpi_data.active_destinations
        building.available_for_distribution_kwh = kpi_data.available_for_distribution_kwh
        building.unused_percent = kpi_data.unused_percent

        db.commit()
        db.refresh(building)
        return BuildingEnergyDashboardResponse.from_orm(building)
    
    @staticmethod
    def get_building_by_id(db: Session, building_id: int) -> Building:
        building = db.query(Building).filter(Building.id == building_id).first()
        if not building:
            raise HTTPException(status_code=404, detail="Building not found")
        return building

    @staticmethod
    def delete_building(db: Session, building_id: int) -> None:
        building = db.query(Building).filter(Building.id == building_id).first()
        if not building:
            raise HTTPException(status_code=404, detail="Building not found")
        db.delete(building)
        db.commit()

    @staticmethod
    def update_building_energy_top_kpi(db: Session, kpi_id: int, kpi_data: BuildingEnergyTopKPICreate) -> BuildingEnergyDashboardResponse:
        building = db.query(Building).filter(Building.id == kpi_id).first()
        if not building:
            raise HTTPException(status_code=404, detail="Building not found")
        
        building.surplus_available_kwh = kpi_data.surplus_available_kwh
        building.surplus_vs_daily_avg_percent = kpi_data.surplus_vs_daily_avg_percent
        building.currently_distributed_kwh = kpi_data.currently_distributed_kwh
        building.active_destinations = kpi_data.active_destinations
        building.available_for_distribution_kwh = kpi_data.available_for_distribution_kwh
        building.unused_percent = kpi_data.unused_percent

        db.commit()
        db.refresh(building)
        return BuildingEnergyDashboardResponse.from_orm(building)
