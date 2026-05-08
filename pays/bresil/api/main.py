from fastapi import FastAPI
from contextlib import asynccontextmanager
from api.db.database import init_db
from api.routes import lots, mesures
from api.services.mqtt_subscriber import start_mqtt


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    start_mqtt()
    yield


app = FastAPI(
    title="FutureKawa API — Brésil",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(lots.router, prefix="/lots", tags=["Lots"])
app.include_router(mesures.router, prefix="/mesures", tags=["Mesures"])


@app.get("/health")
async def health():
    return {"status": "ok", "pays": "bresil"}
