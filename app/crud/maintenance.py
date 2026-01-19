from app.models.maintenance import Maintenance
from app.schemas.maintenance import MaintenanceCreate, MaintenanceHistoryItem
from app import SessionLocal, get_db, HTTPException, Depends
from app.schemas.maintenance import MaintenanceComplete, MaintenanceDashboardResponse
from sqlalchemy.orm import Session



class CrudMaintenance:
    
    @staticmethod
    def create_maintenance(db: Session, maintenance: MaintenanceCreate):
        db_maintenance = Maintenance(
            name=maintenance.name,
            operating_hours=maintenance.operating_hours,
            last_maintenance_date=maintenance.last_maintenance_date,
            next_maintenance_date=maintenance.next_maintenance_date,
            is_overdue=maintenance.is_overdue,
            reliability_percent=maintenance.reliability_percent,
            status=maintenance.status
        )
        db.add(db_maintenance)
        db.commit()
        db.refresh(db_maintenance)
        return db_maintenance

    @staticmethod
    def create_component_maintenance(db: Session, component_maintenance: MaintenanceCreate):
        db_component_maintenance = Maintenance(
            name=component_maintenance.name,
            operating_hours=component_maintenance.operating_hours,
            last_maintenance_date=component_maintenance.last_maintenance_date,
            next_maintenance_date=component_maintenance.next_maintenance_date,
            is_overdue=component_maintenance.is_overdue,
            reliability_percent=component_maintenance.reliability_percent,
            status=component_maintenance.status
        )
        db.add(db_component_maintenance)
        db.commit()
        db.refresh(db_component_maintenance)
        return db_component_maintenance

    @staticmethod
    def complete_maintenance(db: Session, maintenance_id: int, maintenance_complete: MaintenanceComplete):
        db_maintenance = db.query(Maintenance).filter(Maintenance.id == maintenance_id).first()
        if not db_maintenance:
            raise HTTPException(status_code=404, detail="Maintenance record not found")
        
        db_maintenance.completed_at = maintenance_complete.completed_at
        db_maintenance.notes = maintenance_complete.notes
        db.commit()
        db.refresh(db_maintenance)
        return db_maintenance
    
    @staticmethod
    def get_maintenance_history(db: Session, component_id: int) -> list[MaintenanceHistoryItem]:
        maintenances = db.query(Maintenance).filter(Maintenance.component_id == component_id).all()
        return [MaintenanceHistoryItem.from_orm(maintenance) for maintenance in maintenances]
    
    @staticmethod
    def get_all_maintenances(db: Session) -> list:
        maintenances = db.query(Maintenance).all()
        return [maintenance for maintenance in maintenances]
    
    @staticmethod
    def maintenance_dashboard(db: Session) -> MaintenanceDashboardResponse:
        # Placeholder implementation for dashboard data
        kpis = {
            "operating_hours": 1000,
            "total_trips": 150,
            "last_maintenance_date": "2024-01-01T00:00:00",
            "next_maintenance_date": "2024-06-01T00:00:00"
        }
        
        components = db.query(Maintenance).all()
        component_maintenances = [comp for comp in components]
        
        history_items = db.query(Maintenance).all()
        history = [MaintenanceHistoryItem.from_orm(item) for item in history_items]
        
        dashboard_response = MaintenanceDashboardResponse(
            kpis=kpis,
            components=component_maintenances,
            history=history
        )
        
        return dashboard_response
    
    @staticmethod
    def delete_maintenance(db: Session, maintenance_id: int):
        db_maintenance = db.query(Maintenance).filter(Maintenance.id == maintenance_id).first()
        if not db_maintenance:
            raise HTTPException(status_code=404, detail="Maintenance record not found")
        db.delete(db_maintenance)
        db.commit()