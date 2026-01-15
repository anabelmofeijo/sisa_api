from app import Column, Integer, DateTime, Text, Float, Boolean
from app import func
from app import Base
from sqlalchemy import Enum as SqlEnum  
from app.schemas.maintenance import MaintenanceType, MaintenanceStatus


class Maintenance(Base):
    __tablename__ = "maintenances"

    id = Column(Integer, primary_key=True, index=True)

    component_id = Column(Integer, nullable=False)  # opcional: pode criar ForeignKey se houver tabela de componentes
    maintenance_type = Column(SqlEnum(MaintenanceType), nullable=False)
    
    scheduled_date = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    notes = Column(Text, nullable=True)
    status = Column(SqlEnum(MaintenanceStatus), nullable=True)  # status pode ser calculado depois
    
    operating_hours = Column(Integer, nullable=True)
    total_trips = Column(Integer, nullable=True)
    
    last_maintenance_date = Column(DateTime(timezone=True), nullable=True)
    next_maintenance_date = Column(DateTime(timezone=True), nullable=True)
    
    reliability_percent = Column(Float, nullable=True)
    is_overdue = Column(Boolean, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())