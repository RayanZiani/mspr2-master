from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from api.auth import require_role, require_user
from api.db.database import engine
from api.routes import alertes, auth, mesures, stocks, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(
    title="FutureKawa API — Siège",
    version="1.0.0",
    lifespan=lifespan,
)

# Configuration CORS permissive pour le développement et la production
# Autorise toutes les origines onrender.com et localhost
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.onrender\.com|http://localhost:\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(
    users.router,
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(require_role("ADMIN"))],
)
app.include_router(
    stocks.router,
    prefix="/stocks",
    tags=["Stocks"],
    dependencies=[Depends(require_user)],
)
app.include_router(
    mesures.router,
    prefix="/mesures",
    tags=["Mesures"],
    dependencies=[Depends(require_user)],
)
app.include_router(
    alertes.router,
    prefix="/alertes",
    tags=["Alertes"],
    dependencies=[Depends(require_user)],
)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "siege", "source": "mysql"}


@app.get("/health/db")
async def health_db():
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"ok": True}
    except Exception as e:
        # On évite de renvoyer toute la stacktrace; l'UI a juste besoin d'un booléen.
        return {"ok": False, "error": str(e)}
