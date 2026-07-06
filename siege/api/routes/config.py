"""Configuration des seuils IoT par pays."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from api.auth import require_user
from api.db.database import SessionLocal
from api.permissions import UserPermissions
from api.services.redis_cache import STOCKS_CACHE_PREFIX, delete_cache_prefix
from api.services.threshold_service import (
    list_pays_seuils,
    seuils_to_dict,
    update_pays_seuils,
)
from api.services.webhook_service import DISCORD_WEBHOOK_URL, send_test_webhook

router = APIRouter()

_FORBIDDEN_SEUILS_MSG = "Modification des seuils non autorisee pour ce pays"
_FORBIDDEN_SUPER_ADMIN_MSG = "Acces reserve au super administrateur"
_NOT_FOUND_PAYS_MSG = "Pays inconnu"
_UNCONFIGURED_WEBHOOK_MSG = "DISCORD_WEBHOOK_URL non configure"

_FORBIDDEN_SEUILS = {"description": _FORBIDDEN_SEUILS_MSG}
_FORBIDDEN_SUPER_ADMIN = {"description": _FORBIDDEN_SUPER_ADMIN_MSG}
_NOT_FOUND_PAYS = {"description": _NOT_FOUND_PAYS_MSG}
_UNPROCESSABLE_SEUILS = {"description": "Seuils invalides"}
_SERVICE_UNAVAILABLE = {"description": _UNCONFIGURED_WEBHOOK_MSG}


class SeuilsUpdate(BaseModel):
    """Corps de requête pour la mise à jour des seuils IoT d'un pays."""

    temperature_min: float = Field(..., description="Seuil minimum temperature (C)")
    temperature_max: float = Field(..., description="Seuil maximum temperature (C)")
    humidity_min: float = Field(..., ge=0, le=100)
    humidity_max: float = Field(..., ge=0, le=100)


class WebhookStatus(BaseModel):
    """État de configuration du webhook Discord."""

    discord_configured: bool


@router.get("/seuils")
async def get_seuils(_user: Annotated[dict, Depends(require_user)]):
    """Liste les seuils min/max par pays (lecture pour tous les utilisateurs authentifies)."""
    async with SessionLocal() as session:
        rows = await list_pays_seuils(session)
    return [seuils_to_dict(row) for row in rows]


@router.patch(
    "/seuils/{code}",
    responses={
        403: _FORBIDDEN_SEUILS,
        422: _UNPROCESSABLE_SEUILS,
        404: _NOT_FOUND_PAYS,
    },
)
async def patch_seuils(
    code: str,
    body: SeuilsUpdate,
    user: Annotated[dict, Depends(require_user)],
):
    """Met à jour les seuils IoT d'un pays."""
    perms = UserPermissions.from_jwt_user(user)
    if not perms.can_config_iot_thresholds_for(code):
        raise HTTPException(
            status_code=403,
            detail=_FORBIDDEN_SEUILS_MSG,
        )

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
        raise HTTPException(status_code=404, detail=_NOT_FOUND_PAYS_MSG)

    await delete_cache_prefix(STOCKS_CACHE_PREFIX)
    return seuils_to_dict(updated)


@router.get(
    "/webhooks/status",
    response_model=WebhookStatus,
    responses={403: _FORBIDDEN_SUPER_ADMIN},
)
async def webhook_status(user: Annotated[dict, Depends(require_user)]):
    """Indique si le webhook Discord est configuré (super admin uniquement)."""
    perms = UserPermissions.from_jwt_user(user)
    if not perms.can_manage_global_webhook():
        raise HTTPException(status_code=403, detail=_FORBIDDEN_SUPER_ADMIN_MSG)
    return WebhookStatus(discord_configured=bool(DISCORD_WEBHOOK_URL))


@router.post(
    "/webhooks/test",
    responses={403: _FORBIDDEN_SUPER_ADMIN, 503: _SERVICE_UNAVAILABLE},
)
async def webhook_test(user: Annotated[dict, Depends(require_user)]):
    """Envoie un message de test sur le webhook Discord."""
    perms = UserPermissions.from_jwt_user(user)
    if not perms.can_manage_global_webhook():
        raise HTTPException(status_code=403, detail=_FORBIDDEN_SUPER_ADMIN_MSG)
    if not DISCORD_WEBHOOK_URL:
        raise HTTPException(status_code=503, detail=_UNCONFIGURED_WEBHOOK_MSG)
    await send_test_webhook(triggered_by=str(user.get("sub") or "inconnu"))
    return {"ok": True, "discord_configured": True}
