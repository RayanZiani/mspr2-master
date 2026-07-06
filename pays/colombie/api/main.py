"""Application FastAPI FutureKawa — Colombie."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.db.database import init_db
from api.routes import alertes, capteurs, lots, mesures, webhooks
from api.services.mqtt_subscriber import start_mqtt
from api.services.notification_scheduler import start_digest_scheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_application: FastAPI):
    """Initialise la base et le subscriber MQTT au démarrage."""
    await init_db()
    try:
        start_mqtt()
        start_digest_scheduler()
    except OSError:
        logger.exception("Failed to start MQTT subscriber; continuing without it")
    yield


app = FastAPI(
    title="FutureKawa API — Colombie",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(lots.router, prefix="/lots", tags=["Lots"])
app.include_router(mesures.router, prefix="/mesures", tags=["Mesures"])
app.include_router(alertes.router, prefix="/alertes", tags=["Alertes"])
app.include_router(capteurs.router, prefix="/capteurs", tags=["Capteurs"])
app.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])


@app.get("/health")
async def health():
    """Health check public."""
    return {"status": "ok", "pays": "colombie"}
