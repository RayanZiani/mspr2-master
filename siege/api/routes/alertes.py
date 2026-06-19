from typing import Annotated

from fastapi import APIRouter, Depends
from api.services.data_service import get_alertes_grouped
from api.auth import require_user
from api.permissions import UserPermissions

router = APIRouter()


@router.get("/")
async def get_all_alertes(user: Annotated[dict, Depends(require_user)]):
    perms = UserPermissions.from_jwt_user(user)
    grouped = await get_alertes_grouped()
    allowed = perms.allowed_pays_slugs()
    if allowed is None:
        return grouped
    return [block for block in grouped if block.get("pays") in allowed]
