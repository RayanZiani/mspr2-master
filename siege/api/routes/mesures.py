from fastapi import APIRouter, HTTPException
from api.services.data_service import get_mesures_for_lot

router = APIRouter()


@router.get("/")
async def get_all_mesures(lot_id: str | None = None):
    if not lot_id:
        raise HTTPException(
            status_code=400,
            detail="Paramètre lot_id requis pour récupérer les relevés",
        )
    return await get_mesures_for_lot(lot_id)
