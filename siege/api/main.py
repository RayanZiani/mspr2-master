from fastapi import FastAPI
from api.routes import stocks, mesures, alertes

app = FastAPI(
    title="FutureKawa API — Siège",
    version="1.0.0",
)

app.include_router(stocks.router, prefix="/stocks", tags=["Stocks"])
app.include_router(mesures.router, prefix="/mesures", tags=["Mesures"])
app.include_router(alertes.router, prefix="/alertes", tags=["Alertes"])


@app.get("/health")
async def health():
    return {"status": "ok", "service": "siege"}
