from app.models.energy import Energy
from app.schemas.energy import EnergyCreate, EnergyResponse
from app import SessionLocal, get_db, HTTPException, Depends
from sqlalchemy.orm import Session


class EnergyCRUD:
    @staticmethod
    def create_energy(db: Session, energy: EnergyCreate) -> EnergyResponse:
        db_energy = Energy(
            energy_generated=energy.energy_generated,
            energy_consumed=energy.energy_consumed,
            energy_stored=energy.energy_stored,
            energy_origin=energy.energy_origin,
            created_at=energy.created_at
        )
        db.add(db_energy)
        db.commit()
        db.refresh(db_energy)
        return EnergyResponse.from_orm(db_energy)

    @staticmethod
    def get_energy(db: Session, energy_id: int) -> EnergyResponse:
        db_energy = db.query(Energy).filter(Energy.id == energy_id).first()
        if not db_energy:
            raise HTTPException(status_code=404, detail="Energy record not found")
        return EnergyResponse.from_orm(db_energy)

    @staticmethod
    def get_all_energy(db: Session) -> list[EnergyResponse]:
        energies = db.query(Energy).all()
        return [EnergyResponse.from_orm(energy) for energy in energies]