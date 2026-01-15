from app import Column, Integer, DateTime, Float
from app import func
from app import Base
from sqlalchemy import Enum as SqlEnum
from app.schemas.battery import BateryType, Statustype, Healthtype



class Battery(Base):
    __tablename__ = "batteries"

    id = Column(Integer, primary_key=True, index=True)

    battery_name = Column(SqlEnum(BateryType), nullable=False)

    status = Column(SqlEnum(Statustype), nullable=False)

    percentage = Column(Float, nullable=False)

    health = Column(SqlEnum(Healthtype), nullable=False)

    temperature = Column(Float, nullable=False)

    voltage = Column(Float, nullable=False)

    current = Column(Float, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())