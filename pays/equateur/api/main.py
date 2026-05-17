"""FastAPI app for FutureKawa — Équateur

Refactor: add logging and tolerate MQTT startup errors so the API
remains available even if the broker is temporarily unreachable.
"""

import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from api.db.database import init_db
from api.routes import lots, mesures
from api.services.mqtt_subscriber import start_mqtt


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    try:
        start_mqtt()
    except Exception:
        logger.exception("Failed to start MQTT subscriber; continuing without it")
    yield


app = FastAPI(
    title="FutureKawa API — Équateur",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(lots.router, prefix="/lots", tags=["Lots"])
app.include_router(mesures.router, prefix="/mesures", tags=["Mesures"])


@app.get("/health")
async def health():
    return {"status": "ok", "pays": "equateur"}
