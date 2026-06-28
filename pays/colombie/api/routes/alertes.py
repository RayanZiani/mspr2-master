"""Routes REST pour les alertes de lots — Colombie."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from api.db.database import get_session
from api.models.lot import Lot

router = APIRouter()


@router.get("/")
async def list_alertes(session: Annotated[AsyncSession, Depends(get_session)]):
    """Liste les lots en statut alerte ou périmé."""
    result = await session.execute(
        select(Lot)
        .where(Lot.statut != "conforme")
        .order_by(Lot.date_stockage.asc())
    )
    return result.scalars().all()
