from fastapi import FastAPI, APIRouter, Depends, HTTPException
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
from app.core.config import Base, SessionLocal, get_db, engine, local_engine


def CreateDatabaseTables():
    Base.metadata.create_all(bind=engine)
    if local_engine is not None:
        Base.metadata.create_all(bind=local_engine)
