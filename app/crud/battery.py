from app.models.battery import Battery
from app.schemas.battery import BatteryCreate, BatteryResponse, BateryType
from app import SessionLocal, get_db, HTTPException, Depends
from sqlalchemy.orm import Session  
from datetime import datetime


class BatteryCRUD:
    @staticmethod
    def _normalize_battery_payload(battery: BatteryCreate) -> dict:
        payload = battery.model_dump()

        # Batery B arrives from the legacy sender with the voltage/current
        # pair and the percentage/temperature pair inverted.
        if battery.battery_name == BateryType.second_batery:
            payload["percentage"], payload["temperature"] = (
                payload["temperature"],
                payload["percentage"],
            )
            payload["voltage"], payload["current"] = (
                payload["current"],
                payload["voltage"],
            )

        return payload

    @staticmethod
    def create_battery(db: Session, battery: BatteryCreate) -> BatteryResponse:
        normalized_battery = BatteryCRUD._normalize_battery_payload(battery)
        db_battery = Battery(
            battery_name=normalized_battery["battery_name"],
            status=normalized_battery["status"],
            percentage=normalized_battery["percentage"],
            health=normalized_battery["health"],
            temperature=normalized_battery["temperature"],
            voltage=normalized_battery["voltage"],
            current=normalized_battery["current"],
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
