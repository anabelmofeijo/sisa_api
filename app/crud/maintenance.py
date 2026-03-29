from app.models.maintenance import Maintenance
from app.schemas.maintenance import MaintenanceCreate, MaintenanceStatus, MaintenanceType
from app import HTTPException
from app.schemas.maintenance import MaintenanceComplete
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

MAINTENANCE_INTERVAL_DAYS = 30  # 1 mês
DEFAULT_MAINTENANCE_COMPONENTS = [
    {
        "component_id": 1,
        "name": "Motor",
        "maintenance_type": MaintenanceType.preventive,
        "operating_hours": 8234,
        "total_trips": 31146,
        "reliability_percent": 98.0,
        "status": MaintenanceStatus.optimal
    },
    {
        "component_id": 2,
        "name": "Inversor",
        "maintenance_type": MaintenanceType.preventive,
        "operating_hours": 8234,
        "total_trips": 31147,
        "reliability_percent": 96.0,
        "status": MaintenanceStatus.optimal
    },
    {
        "component_id": 3,
        "name": "Sistema Regenerativo",
        "maintenance_type": MaintenanceType.corrective,
        "operating_hours": 8234,
        "total_trips": 31147,
        "reliability_percent": 74.0,
        "status": MaintenanceStatus.warning
    },
    {
        "component_id": 4,
        "name": "Controlador de Baterias",
        "maintenance_type": MaintenanceType.preventive,
        "operating_hours": 8234,
        "total_trips": 31147,
        "reliability_percent": 94.0,
        "status": MaintenanceStatus.warning
    }
]


class CrudMaintenance:

    @staticmethod
    def get_default_component(component_id: int):
        for component in DEFAULT_MAINTENANCE_COMPONENTS:
            if component["component_id"] == component_id:
                return component
        return None

    @staticmethod
    def ensure_monthly_maintenance(db: Session):
        """Garante um registo de manutenção por componente no mês atual."""
        now = datetime.now()
        month_start = datetime(now.year, now.month, 1)
        if now.month == 12:
            next_month_start = datetime(now.year + 1, 1, 1)
        else:
            next_month_start = datetime(now.year, now.month + 1, 1)

        existing_component_ids = [
            component_id
            for (component_id,) in db.query(Maintenance.component_id).distinct().all()
            if component_id is not None
        ]
        default_component_ids = [component["component_id"] for component in DEFAULT_MAINTENANCE_COMPONENTS]
        component_ids = sorted(set(existing_component_ids + default_component_ids))

        created = False

        for component_id in component_ids:
            current_month_item = (
                db.query(Maintenance)
                .filter(Maintenance.component_id == component_id)
                .filter(Maintenance.scheduled_date >= month_start)
                .filter(Maintenance.scheduled_date < next_month_start)
                .first()
            )

            if current_month_item:
                continue

            latest_item = (
                db.query(Maintenance)
                .filter(Maintenance.component_id == component_id)
                .order_by(Maintenance.scheduled_date.desc(), Maintenance.id.desc())
                .first()
            )

            default_component = CrudMaintenance.get_default_component(component_id)

            scheduled_date = latest_item.next_maintenance_date if latest_item else month_start
            if scheduled_date < month_start or scheduled_date >= next_month_start:
                scheduled_date = month_start

            db.add(
                Maintenance(
                    component_id=component_id,
                    maintenance_type=(
                        latest_item.maintenance_type
                        if latest_item
                        else default_component["maintenance_type"]
                    ),
                    scheduled_date=scheduled_date,
                    completed_at=None,
                    notes=(
                        default_component["name"]
                        if default_component
                        else "Agendamento mensal automático"
                    ),
                    status=(
                        latest_item.status
                        if latest_item and latest_item.status
                        else default_component["status"] if default_component else MaintenanceStatus.warning
                    ),
                    operating_hours=(
                        latest_item.operating_hours
                        if latest_item and latest_item.operating_hours is not None
                        else default_component["operating_hours"] if default_component else 0
                    ),
                    total_trips=(
                        latest_item.total_trips
                        if latest_item and latest_item.total_trips is not None
                        else default_component["total_trips"] if default_component else 0
                    ),
                    last_maintenance_date=latest_item.last_maintenance_date if latest_item else None,
                    next_maintenance_date=scheduled_date + timedelta(days=MAINTENANCE_INTERVAL_DAYS),
                    reliability_percent=(
                        latest_item.reliability_percent
                        if latest_item and latest_item.reliability_percent is not None
                        else default_component["reliability_percent"] if default_component else 0.0
                    ),
                    is_overdue=False
                )
            )
            created = True

        if created:
            db.commit()

    @staticmethod
    def get_pending_maintenance(db: Session):
        """Retorna manutenção pendente (não concluída)."""
        CrudMaintenance.ensure_monthly_maintenance(db)
        return (
            db.query(Maintenance)
            .filter(Maintenance.completed_at == None)
            .order_by(Maintenance.scheduled_date)
            .all()
        )

    @staticmethod
    def create_component(db: Session, data: MaintenanceCreate):
        component = Maintenance(
            component_id=data.component_id,
            maintenance_type=data.maintenance_type,
            scheduled_date=data.scheduled_date,
            notes=data.notes,
            completed_at=None
        )
        db.add(component)
        db.commit()
        db.refresh(component)
        return component

    @staticmethod
    def complete_maintenance(
        db: Session,
        maintenance_id: int,
        data: MaintenanceComplete
    ):
        component = db.query(Maintenance).filter(Maintenance.id == maintenance_id).first()

        if not component:
            raise HTTPException(status_code=404, detail="Componente não encontrado")

        completed_time = data.completed_at or datetime.now()

        component.completed_at = completed_time
        component.last_maintenance_date = completed_time
        component.next_maintenance_date = completed_time + timedelta(days=MAINTENANCE_INTERVAL_DAYS)
        component.is_overdue = False
        component.status = MaintenanceStatus.optimal

        if data.notes:
            component.notes = data.notes

        db.commit()
        db.refresh(component)
        return component
