from app import BaseModel, datetime, Optional, Dict


# Dashboard Energy Schemas

class ActiveEnergyCreate(BaseModel):
    id: int
    elevator: bool
    painel: bool
    created_at: Optional[datetime] = None


class ActiveEnergyResponse(BaseModel):
    id: int
    elevator: bool  
    painel: bool
    
    class Config:
        orm_mode = True

class BuildingEnergyCreate(BaseModel):
    id: int
    supplied_energy: float
    main_destination: str
    created_at: Optional[datetime] = None

class BuildingEnergyResponse(BaseModel):
    id: int
    supplied_energy: float  
    main_destination: str
    
    class Config:
        orm_mode = True

# Energy Schemas

class EnergyCreate(BaseModel):
    id: int
    energy_generated: float
    energy_consumed: float
    energy_stored: float
    energy_origin: Dict[str, float]
    created_at: Optional[datetime] = None

class EnergyResponse(BaseModel):
    id: int
    energy_generated: float  
    energy_consumed: float
    energy_stored: float
    energy_origin: Dict[str, float]
    
    class Config:
        orm_mode = True

