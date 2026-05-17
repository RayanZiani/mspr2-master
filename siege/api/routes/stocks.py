from fastapi import APIRouter
from api.services.data_service import get_stocks_grouped

router = APIRouter()


@router.get("/")
async def get_all_stocks():
    return await get_stocks_grouped()
