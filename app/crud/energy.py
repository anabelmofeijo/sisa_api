from app.models.energy import Energy
from app.models.battery import Battery
from app.schemas.energy import EnergyCreate, EnergyResponse
from app import SessionLocal, get_db, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from app.schemas.battery import BateryType, Statustype

ENERGY_REFRESH_SECONDS = 60
BATTERY_CAPACITY_KWH = 5.0

class EnergyCRUD:
    @staticmethod
    def _latest_battery_by_name(db: Session, battery_name: BateryType):
        return (
            db.query(Battery)
            .filter(Battery.battery_name == battery_name)
            .order_by(Battery.created_at.desc(), Battery.id.desc())
            .first()
        )

    @staticmethod
    def _calculate_energy_from_batteries(first_battery: Battery | None, second_battery: Battery | None):
        batteries = [battery for battery in [first_battery, second_battery] if battery is not None]
        if not batteries:
            return None

        generated = 0.0
        consumed = 0.0
        stored = 0.0

        for battery in batteries:
            power_kw = max((battery.voltage or 0) * abs(battery.current or 0) / 1000.0, 0.0)
            stored += max(min((battery.percentage or 0), 100), 0) / 100.0 * BATTERY_CAPACITY_KWH

            if battery.status in (Statustype.charging, Statustype.full, Statustype.not_charging):
                generated += power_kw
            elif battery.status == Statustype.discharging:
                consumed += power_kw

        return EnergyCreate(
            energy_generated=round(generated, 3),
            energy_consumed=round(consumed, 3),
            energy_stored=round(stored, 3),
            energy_origin={
                "panel": round(generated, 3),
                "regeneration": 0.0
            }
        )

    @staticmethod
    def ensure_recent_energy_snapshot(db: Session):
        latest_energy = (
            db.query(Energy)
            .order_by(Energy.created_at.desc(), Energy.id.desc())
            .first()
        )

        if latest_energy and latest_energy.created_at:
            age_seconds = (datetime.utcnow() - latest_energy.created_at.replace(tzinfo=None)).total_seconds()
            if age_seconds < ENERGY_REFRESH_SECONDS:
                return latest_energy

        first_battery = EnergyCRUD._latest_battery_by_name(db, BateryType.first_batery)
        second_battery = EnergyCRUD._latest_battery_by_name(db, BateryType.second_batery)
        calculated_energy = EnergyCRUD._calculate_energy_from_batteries(first_battery, second_battery)

        if not calculated_energy:
            return latest_energy

        return EnergyCRUD.create_energy(db, calculated_energy)

    @staticmethod
    def create_energy(db: Session, energy: EnergyCreate) -> EnergyResponse:
        db_energy = Energy(
            energy_generated=energy.energy_generated,
            energy_consumed=energy.energy_consumed,
            energy_stored=energy.energy_stored,
            energy_origin=energy.energy_origin,
            created_at= datetime.utcnow() 
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
        EnergyCRUD.ensure_recent_energy_snapshot(db)
        energies = db.query(Energy).all()
        return [EnergyResponse.from_orm(energy) for energy in energies]
