"""Routes d'agrégation des stocks par pays."""

from typing import Annotated

from fastapi import APIRouter, Depends

from api.auth import require_user
from api.permissions import UserPermissions
from api.services.data_service import get_stocks_grouped

router = APIRouter()


@router.get("/")
async def get_all_stocks(user: Annotated[dict, Depends(require_user)]):
    """Liste les stocks groupés par pays, filtrés selon les permissions."""
    perms = UserPermissions.from_jwt_user(user)
    grouped = await get_stocks_grouped()
    allowed = perms.allowed_pays_slugs()
    if allowed is None:
        return grouped
    return [block for block in grouped if block.get("pays") in allowed]
