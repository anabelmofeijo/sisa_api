from app import Column, Integer, String, DateTime
from app import func
from app import Base
from app import JSON, Float, Boolean



class ActiveEnergy(Base):
    __tablename__ = "active_energy"

    id = Column(Integer, primary_key=True, index=True)

    elevator = Column(Boolean, nullable=False)
    painel = Column(Boolean, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class BuildingEnergy(Base):
    __tablename__ = "building_energy"

    id = Column(Integer, primary_key=True, index=True)

    supplied_energy = Column(Float, nullable=False)
    main_destination = Column(String(100), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Energy(Base):
    __tablename__ = "energy"

    id = Column(Integer, primary_key=True, index=True)

    energy_generated = Column(Float, nullable=False)
    energy_consumed = Column(Float, nullable=False)
    energy_stored = Column(Float, nullable=False)

    # Dictionary like: {"solar": 4.5, "grid": 2.1, "generator": 1.0}
    energy_origin = Column(JSON, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())