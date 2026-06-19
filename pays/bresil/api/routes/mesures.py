from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from api.db.database import get_session
from api.models.mesure import Mesure

router = APIRouter()


@router.get("/")
async def list_mesures(
    session: Annotated[AsyncSession, Depends(get_session)],
    lot_id: str | None = None,
):
    query = select(Mesure).order_by(Mesure.timestamp.desc())
    if lot_id:
        query = query.where(Mesure.lot_id == lot_id)
    result = await session.execute(query)
    return result.scalars().all()
