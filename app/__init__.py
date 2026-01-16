from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Literal, Optional, Dict
from datetime import datetime
from enum import Enum
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import JSON, Float, Boolean, Text, Integer, Enum as SqlEnum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Float,
    ForeignKey
)
from app.core.config import Base, db, SessionLocal, Session


def CreateDatabaseTables():
    Base.metadata.create_all(bind=db.get_bind())