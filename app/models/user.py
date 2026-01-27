from app import Column, Integer, String, DateTime
from app import func
from app import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)
    lastname = Column(String(100), nullable=False)

    email = Column(String(150), unique=True, index=True, nullable=False)

    building = Column(String(100), nullable=False)

    password = Column(String(255), nullable=False)

    phone = Column(String(30), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())