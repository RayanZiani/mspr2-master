"""Routes REST pour la gestion des lots — Colombie."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from api.db.database import get_session
from api.models.lot import Lot

router = APIRouter()


def _lot_to_dict(lot: Lot) -> dict[str, Any]:
    return {
        "id": lot.id,
        "pays": lot.pays,
        "exploitation": lot.exploitation,
        "entrepot": lot.entrepot,
        "date_stockage": lot.date_stockage.isoformat() if lot.date_stockage else None,
        "statut": lot.statut,
    }


@router.get("/")
async def list_lots(session: Annotated[AsyncSession, Depends(get_session)]):
    """Liste les lots triés par date de stockage (FIFO)."""
    result = await session.execute(
        select(Lot).order_by(Lot.date_stockage.asc())
    )
    return [_lot_to_dict(lot) for lot in result.scalars().all()]


@router.get("/{lot_id}")
async def get_lot(lot_id: str, session: Annotated[AsyncSession, Depends(get_session)]):
    """Retourne un lot par identifiant."""
    result = await session.execute(select(Lot).where(Lot.id == lot_id))
    lot = result.scalar_one_or_none()
    return _lot_to_dict(lot) if lot else None


@router.post("/")
async def create_lot(lot: dict, session: Annotated[AsyncSession, Depends(get_session)]):
    """Crée un nouveau lot."""
    new_lot = Lot(**lot)
    session.add(new_lot)
    await session.commit()
    return _lot_to_dict(new_lot)
