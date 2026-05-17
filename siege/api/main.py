from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.db.database import engine
from api.routes import stocks, mesures, alertes


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(
    title="FutureKawa API — Siège",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stocks.router, prefix="/stocks", tags=["Stocks"])
app.include_router(mesures.router, prefix="/mesures", tags=["Mesures"])
app.include_router(alertes.router, prefix="/alertes", tags=["Alertes"])


@app.get("/health")
async def health():
    return {"status": "ok", "service": "siege", "source": "mysql"}
