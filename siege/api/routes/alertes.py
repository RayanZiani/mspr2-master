from fastapi import APIRouter
from api.services.data_service import get_alertes_grouped

router = APIRouter()


@router.get("/")
async def get_all_alertes():
    return await get_alertes_grouped()
