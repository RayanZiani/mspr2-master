from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from api.db.database import get_session
from api.models.lot import Lot

router = APIRouter()


@router.get("/")
async def list_alertes(session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Lot)
        .where(Lot.statut != "conforme")
        .order_by(Lot.date_stockage.asc())
    )
    return result.scalars().all()
