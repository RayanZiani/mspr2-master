"""Routes d'agrégation des alertes par pays."""

from typing import Annotated

from fastapi import APIRouter, Depends

from api.auth import require_user
from api.permissions import UserPermissions
from api.services.data_service import get_alertes_grouped

router = APIRouter()


@router.get("/")
async def get_all_alertes(user: Annotated[dict, Depends(require_user)]):
    """Liste les alertes groupées par pays, filtrées selon les permissions."""
    perms = UserPermissions.from_jwt_user(user)
    grouped = await get_alertes_grouped()
    allowed = perms.allowed_pays_slugs()
    if allowed is None:
        return grouped
    return [block for block in grouped if block.get("pays") in allowed]
