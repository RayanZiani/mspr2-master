"""Routes CRUD lots, entrepôts et exploitations."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from api.auth import require_user
from api.permissions import UserPermissions
from api.services import master_data_service as mds

router = APIRouter()


class ExploitationCreate(BaseModel):
    pays_slug: str = Field(..., min_length=2)
    nom: str = Field(..., min_length=1, max_length=255)


class ExploitationUpdate(BaseModel):
    nom: str = Field(..., min_length=1, max_length=255)


class EntrepotCreate(BaseModel):
    pays_slug: str = Field(..., min_length=2)
    nom: str = Field(..., min_length=1, max_length=255)
    adresse: str | None = None
    exploitation_id: int | None = None


class EntrepotUpdate(BaseModel):
    nom: str | None = Field(None, min_length=1, max_length=255)
    adresse: str | None = None
    exploitation_id: int | None = None


class LotCreate(BaseModel):
    exploitation_id: int
    entrepot_id: int


class LotUpdate(BaseModel):
    statut: str | None = None
    expedier: bool = False


def _perms(user: dict) -> UserPermissions:
    return UserPermissions.from_jwt_user(user)


def _forbidden() -> HTTPException:
    return HTTPException(status_code=403, detail="Accès refusé")


def _bad_request(msg: str) -> HTTPException:
    return HTTPException(status_code=400, detail=msg)


def _not_found(msg: str) -> HTTPException:
    return HTTPException(status_code=404, detail=msg)


@router.get("/exploitations")
async def list_exploitations(user: Annotated[dict, Depends(require_user)]):
    perms = _perms(user)
    if not (
        perms.can_write_lots()
        or perms.can_manage_entrepots()
        or perms.can_manage_exploitations()
    ):
        raise _forbidden()
    return await mds.list_exploitations(perms.allowed_pays_slugs())


@router.get("/entrepots")
async def list_entrepots(user: Annotated[dict, Depends(require_user)]):
    perms = _perms(user)
    if not (perms.can_write_lots() or perms.can_manage_entrepots()):
        raise _forbidden()
    return await mds.list_entrepots(perms.allowed_pays_slugs())


@router.post("/exploitations")
async def create_exploitation(
    body: ExploitationCreate,
    user: Annotated[dict, Depends(require_user)],
):
    perms = _perms(user)
    if not perms.can_manage_exploitations():
        raise _forbidden()
    allowed = perms.allowed_pays_slugs()
    slug = body.pays_slug.lower()
    if allowed is not None and slug not in allowed:
        raise _forbidden()
    try:
        return await mds.create_exploitation(slug, body.nom)
    except ValueError as exc:
        raise _bad_request(str(exc)) from exc


@router.patch("/exploitations/{exploitation_id}")
async def patch_exploitation(
    exploitation_id: int,
    body: ExploitationUpdate,
    user: Annotated[dict, Depends(require_user)],
):
    perms = _perms(user)
    if not perms.can_manage_exploitations():
        raise _forbidden()
    try:
        await mds.update_exploitation(exploitation_id, body.nom)
    except ValueError as exc:
        raise _not_found(str(exc)) from exc
    return {"ok": True}


@router.delete("/exploitations/{exploitation_id}")
async def remove_exploitation(
    exploitation_id: int,
    user: Annotated[dict, Depends(require_user)],
):
    perms = _perms(user)
    if not perms.can_manage_exploitations():
        raise _forbidden()
    try:
        await mds.delete_exploitation(exploitation_id)
    except ValueError as exc:
        raise _bad_request(str(exc)) from exc
    return {"ok": True}


@router.post("/entrepots")
async def create_entrepot(
    body: EntrepotCreate,
    user: Annotated[dict, Depends(require_user)],
):
    perms = _perms(user)
    if not perms.can_manage_entrepots():
        raise _forbidden()
    allowed = perms.allowed_pays_slugs()
    slug = body.pays_slug.lower()
    if allowed is not None and slug not in allowed:
        raise _forbidden()
    try:
        return await mds.create_entrepot(slug, body.nom, body.exploitation_id, body.adresse)
    except ValueError as exc:
        raise _bad_request(str(exc)) from exc


@router.patch("/entrepots/{entrepot_id}")
async def patch_entrepot(
    entrepot_id: int,
    body: EntrepotUpdate,
    user: Annotated[dict, Depends(require_user)],
):
    perms = _perms(user)
    if not perms.can_manage_entrepots():
        raise _forbidden()
    try:
        await mds.update_entrepot(entrepot_id, body.nom, body.adresse, body.exploitation_id)
    except ValueError as exc:
        raise _not_found(str(exc)) from exc
    return {"ok": True}


@router.delete("/entrepots/{entrepot_id}")
async def remove_entrepot(
    entrepot_id: int,
    user: Annotated[dict, Depends(require_user)],
):
    perms = _perms(user)
    if not perms.can_manage_entrepots():
        raise _forbidden()
    try:
        await mds.delete_entrepot(entrepot_id)
    except ValueError as exc:
        raise _bad_request(str(exc)) from exc
    return {"ok": True}


@router.get("/lots")
async def list_lots_manage(user: Annotated[dict, Depends(require_user)]):
    perms = _perms(user)
    if not perms.can_write_lots():
        raise _forbidden()
    return await mds.list_lots_manage(perms.allowed_pays_slugs())


@router.post("/lots")
async def create_lot(
    body: LotCreate,
    user: Annotated[dict, Depends(require_user)],
):
    perms = _perms(user)
    if not perms.can_write_lots():
        raise _forbidden()
    try:
        return await mds.create_lot(
            body.exploitation_id,
            body.entrepot_id,
            allowed_slugs=perms.allowed_pays_slugs(),
        )
    except ValueError as exc:
        raise _bad_request(str(exc)) from exc


@router.patch("/lots/{lot_id}")
async def patch_lot(
    lot_id: str,
    body: LotUpdate,
    user: Annotated[dict, Depends(require_user)],
):
    perms = _perms(user)
    if not perms.can_write_lots():
        raise _forbidden()
    slug = await mds.get_lot_pays_slug_by_id(lot_id)
    if not slug:
        raise _not_found("Lot introuvable")
    allowed = perms.allowed_pays_slugs()
    if allowed is not None and slug not in allowed:
        raise _forbidden()
    try:
        await mds.update_lot(lot_id, body.statut, body.expedier)
    except ValueError as exc:
        raise _bad_request(str(exc)) from exc
    return {"ok": True}
