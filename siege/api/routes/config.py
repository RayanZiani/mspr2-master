"""Configuration des seuils IoT par pays."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from api.auth import require_role, require_user
from api.db.database import SessionLocal
from api.permissions import UserPermissions
from api.services.redis_cache import delete_cache_prefix
from api.services.threshold_service import (
    get_pays_seuils,
    list_pays_seuils,
    seuils_to_dict,
    update_pays_seuils,
)
from api.services.webhook_service import DISCORD_WEBHOOK_URL, notify

router = APIRouter()


class SeuilsUpdate(BaseModel):
    temperature_min: float = Field(..., description="Seuil minimum temperature (C)")
    temperature_max: float = Field(..., description="Seuil maximum temperature (C)")
    humidity_min: float = Field(..., ge=0, le=100)
    humidity_max: float = Field(..., ge=0, le=100)


class WebhookStatus(BaseModel):
    discord_configured: bool


@router.get("/seuils")
async def get_seuils(_user: dict = Depends(require_user)):
    """Liste les seuils min/max par pays (lecture pour tous les utilisateurs authentifies)."""
    async with SessionLocal() as session:
        rows = await list_pays_seuils(session)
    return [seuils_to_dict(row) for row in rows]


@router.patch("/seuils/{code}")
async def patch_seuils(
    code: str,
    body: SeuilsUpdate,
    user: dict = Depends(require_user),
):
    perms = UserPermissions.from_jwt_user(user)
    if not perms.can_config_iot_thresholds():
        raise HTTPException(status_code=403, detail="Seuls les administrateurs peuvent modifier les seuils")

    try:
        async with SessionLocal() as session:
            updated = await update_pays_seuils(
                session,
                code,
                body.temperature_min,
                body.temperature_max,
                body.humidity_min,
                body.humidity_max,
            )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    if updated is None:
        raise HTTPException(status_code=404, detail="Pays inconnu")

    await delete_cache_prefix("siege:stocks")
    return seuils_to_dict(updated)


@router.get("/webhooks/status", response_model=WebhookStatus)
async def webhook_status(user: dict = Depends(require_user)):
    perms = UserPermissions.from_jwt_user(user)
    if not perms.can_config_iot_thresholds():
        raise HTTPException(status_code=403, detail="Acces reserve aux administrateurs")
    return WebhookStatus(discord_configured=bool(DISCORD_WEBHOOK_URL))


@router.post("/webhooks/test")
async def webhook_test(user: dict = Depends(require_user)):
    perms = UserPermissions.from_jwt_user(user)
    if not perms.can_config_iot_thresholds():
        raise HTTPException(status_code=403, detail="Acces reserve aux administrateurs")
    if not DISCORD_WEBHOOK_URL:
        raise HTTPException(status_code=503, detail="DISCORD_WEBHOOK_URL non configure")
    await notify(
        "Test webhook FutureKawa — configuration capteurs / seuils OK.",
        "siege",
        alert_type="condition",
    )
    return {"ok": True, "discord_configured": True}
