from app import BaseModel, datetime, Optional, Dict


# Dashboard Energy Schemas

class ActiveEnergyCreate(BaseModel):
    elevator: bool
    painel: bool


class ActiveEnergyResponse(BaseModel):
    id: int
    elevator: bool  
    painel: bool
    
    model_config = {
        "from_attributes": True
    }

class BuildingEnergyCreate(BaseModel):
    supplied_energy: float
    main_destination: str

class BuildingEnergyResponse(BaseModel):
    id: int
    supplied_energy: float  
    main_destination: str
    
    model_config = {
        "from_attributes": True
    }

# Energy Schemas

class EnergyCreate(BaseModel):
    energy_generated: float
    energy_consumed: float
    energy_stored: float
    energy_origin: Dict[str, float]

class EnergyResponse(BaseModel):
    id: int
    energy_generated: float  
    energy_consumed: float
    energy_stored: float
    energy_origin: Dict[str, float]
    
    model_config = {
        "from_attributes": True
    }

