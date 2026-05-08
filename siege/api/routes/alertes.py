from fastapi import APIRouter
from api.services.aggregator import fetch_all_pays

router = APIRouter()


@router.get("/")
async def get_all_alertes():
    return await fetch_all_pays("alertes")
