from fastapi import APIRouter
from api.services.aggregator import fetch_all_pays

router = APIRouter()


@router.get("/")
async def get_all_mesures(lot_id: str | None = None):
    params = {"lot_id": lot_id} if lot_id else None
    return await fetch_all_pays("mesures", params=params)
