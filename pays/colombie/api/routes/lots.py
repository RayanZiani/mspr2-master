from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from api.db.database import get_session
from api.models.lot import Lot

router = APIRouter()


@router.get("/")
async def list_lots(session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Lot).order_by(Lot.date_stockage.asc())  # tri FIFO
    )
    return result.scalars().all()


@router.get("/{lot_id}")
async def get_lot(lot_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Lot).where(Lot.id == lot_id))
    return result.scalar_one_or_none()


@router.post("/")
async def create_lot(lot: dict, session: AsyncSession = Depends(get_session)):
    new_lot = Lot(**lot)
    session.add(new_lot)
    await session.commit()
    return new_lot
