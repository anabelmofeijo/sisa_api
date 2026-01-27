from app import Column, Integer, String, DateTime, Float
from app import func
from app import Base
from sqlalchemy import Enum as SqlEnum
from app.schemas.alerts import AlertLevel, AlertStatus


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)
    description = Column(String, nullable=False)

    level = Column(SqlEnum(AlertLevel), nullable=False)
    status = Column(SqlEnum(AlertStatus), nullable=False, default=AlertStatus.active)

    device_id = Column(Integer, nullable=True)  # opcional, pode criar ForeignKey se tiver tabela de dispositivos
    measured_value = Column(Float, nullable=True)
    unit = Column(String, nullable=True)

    detected_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ElevatorWorkingAlert(Base):
    __tablename__ = "elevator_working_alerts"

    id = Column(Integer, primary_key=True, index=True)

    elevator_id = Column(Integer, nullable=False)
    is_working = Column(Integer, nullable=False)  # 1 para funcionando, 0 para não funcionando

    reported_at = Column(DateTime(timezone=True), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())