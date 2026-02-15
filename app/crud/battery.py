from app.models.battery import Battery
from app.schemas.battery import BatteryCreate, BatteryResponse
from app import SessionLocal, get_db, HTTPException, Depends
from sqlalchemy.orm import Session  
from datetime import datetime


class BatteryCRUD:
    @staticmethod
    def create_battery(db: Session, battery: BatteryCreate) -> BatteryResponse:
        db_battery = Battery(
            battery_name=battery.battery_name,
            status=battery.status,
            percentage=battery.percentage,
            health=battery.health,
            temperature=battery.temperature,
            voltage=battery.voltage,
            current=battery.current,
            created_at= datetime.utcnow()
        )
        db.add(db_battery)
        db.commit()
        db.refresh(db_battery)
        return BatteryResponse.from_orm(db_battery)

    @staticmethod
    def get_battery(db: Session, battery_id: int) -> BatteryResponse:
        db_battery = db.query(Battery).filter(Battery.id == battery_id).first()
        if not db_battery:
            raise HTTPException(status_code=404, detail="Battery not found")
        return BatteryResponse.from_orm(db_battery)

    @staticmethod
    def get_all_batteries(db: Session) -> list[BatteryResponse]:
        batteries = db.query(Battery).all()
        return [BatteryResponse.from_orm(battery) for battery in batteries]

    @staticmethod
    def get_all_batteries_by_the_name(db: Session, battery_name: str) -> list[BatteryResponse]:
        batteries = db.query(Battery).filter(Battery.battery_name == battery_name).all()
        return [BatteryResponse.from_orm(battery) for battery in batteries]