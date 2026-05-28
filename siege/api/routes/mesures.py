from fastapi import APIRouter, Depends, HTTPException
from api.auth import require_user
from api.permissions import UserPermissions
from api.services.data_service import get_lot_pays_slug, get_mesures_for_lot

router = APIRouter()


@router.get("/")
async def get_all_mesures(lot_id: str | None = None, user: dict = Depends(require_user)):
    if not lot_id:
        raise HTTPException(
            status_code=400,
            detail="Paramètre lot_id requis pour récupérer les relevés",
        )
    perms = UserPermissions.from_jwt_user(user)
    allowed = perms.allowed_pays_slugs()
    if allowed is not None:
        lot_pays = await get_lot_pays_slug(lot_id)
        if not lot_pays:
            raise HTTPException(status_code=404, detail="Lot introuvable")
        if lot_pays not in allowed:
            raise HTTPException(status_code=403, detail="Accès refusé")
    return await get_mesures_for_lot(lot_id)
