from app.models.battery import Battery
from app.schemas.battery import BatteryCreate, BatteryResponse, BateryType
from app import SessionLocal, get_db, HTTPException, Depends
from sqlalchemy.orm import Session  
from datetime import datetime


class BatteryCRUD:
    @staticmethod
    def _latest_battery_by_name(db: Session, battery_name: BateryType) -> Battery | None:
        return (
            db.query(Battery)
            .filter(Battery.battery_name == battery_name)
            .order_by(Battery.created_at.desc(), Battery.id.desc())
            .first()
        )

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

        # The sender includes Batery B's percentage and voltage inside the
        # temperature and current fields of Batery A.
        if battery.battery_name == BateryType.first_batery:
            latest_second_battery = BatteryCRUD._latest_battery_by_name(db, BateryType.second_batery)
            db_second_battery = Battery(
                battery_name=BateryType.second_batery,
                status=latest_second_battery.status if latest_second_battery else battery.status,
                percentage=battery.temperature,
                health=latest_second_battery.health if latest_second_battery else battery.health,
                temperature=latest_second_battery.temperature if latest_second_battery else 0.0,
                voltage=battery.current,
                current=latest_second_battery.current if latest_second_battery else 0.0,
                created_at=datetime.utcnow()
            )
            db.add(db_second_battery)

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
