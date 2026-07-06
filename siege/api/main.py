"""Point d'entrée FastAPI de l'API siège FutureKawa."""

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from api.auth import require_role, require_user
from api.db.database import engine
from api.routes import alertes, auth, config, gestion, mesures, stocks, users


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Libère le pool SQLAlchemy à l'arrêt du service."""
    yield
    await engine.dispose()


app = FastAPI(
    title="FutureKawa API — Siège",
    version="1.0.0",
    lifespan=lifespan,
)

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
    dependencies=[Depends(require_role("SUPER_ADMIN"))],
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
app.include_router(
    config.router,
    prefix="/config",
    tags=["Config"],
)
app.include_router(
    gestion.router,
    prefix="/gestion",
    tags=["Gestion"],
    dependencies=[Depends(require_user)],
)


@app.get("/health")
@app.head("/health")
async def health():
    """Sonde de disponibilité du service."""
    return {"status": "ok", "service": "siege", "source": "mysql"}


@app.get("/health/db")
@app.head("/health/db")
async def health_db():
    """Sonde de connectivité MySQL."""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"ok": True}
    except (SQLAlchemyError, OSError) as exc:
        return {"ok": False, "error": str(exc)}
