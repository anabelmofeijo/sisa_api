from fastapi import FastAPI
from app import CreateDatabaseTables
from app.models import battery, alert, maintenance, building, user, energy
from app.models.alert import ElevatorWorkingAlert
from app import FastAPI, CORSMiddleware
from app.routers import energy, batteries, alerts, maintenance, building, users, logs
from app.routers.alerts import start_alert_monitor, stop_alert_monitor

app = FastAPI(title="SISA API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routers
app.include_router(energy.router, prefix="/energy", tags=["energy"])
app.include_router(batteries.router, prefix="/batery", tags=["batery"])
app.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
app.include_router(maintenance.router, prefix="/maintenance", tags=["maintenance"])
app.include_router(building.router, prefix="/building", tags=["building"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(logs.router, prefix="/logs", tags=["logs"])

CreateDatabaseTables()


@app.on_event("startup")
async def startup_event():
    start_alert_monitor()


@app.on_event("shutdown")
async def shutdown_event():
    await stop_alert_monitor()


@app.get("/")
async def start():
    return {"message": "API is running"}
