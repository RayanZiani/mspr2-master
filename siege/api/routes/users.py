from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import text

from api.auth import hash_password, verify_password
from api.db.database import SessionLocal

router = APIRouter()

VALID_ROLES = frozenset({"ADMIN", "USER"})
VALID_PAYS = frozenset({"SIEGE", "BRESIL", "EQUATEUR", "COLOMBIE"})

_USER_BAD_REQUEST = {"description": "Données utilisateur invalides"}

class CreateUserRequest(BaseModel):
    username: str
    password: str | None = None
    password_hash: str | None = None
    role: str = "USER"  # ADMIN | USER
    pays_code: str | None = None  # SIEGE | BRESIL | EQUATEUR | COLOMBIE
    email: str | None = None


class UpdateUserRequest(BaseModel):
    role: str | None = None
    active: bool | None = None
    password: str | None = None
    password_hash: str | None = None
    pays_code: str | None = None
    email: str | None = None


LIST_SQL = text(
    """
    SELECT id, username, role, active, pays_code, email, last_login_at, last_login_ip, created_at
    FROM user_account
    ORDER BY created_at DESC
    """
)

INSERT_SQL = text(
    """
    INSERT INTO user_account (username, password_hash, role, active, pays_code, email)
    VALUES (:username, :password_hash, :role, 1, :pays_code, :email)
    """
)

UPDATE_SQL = text(
    """
    UPDATE user_account
    SET
      role = COALESCE(:role, role),
      active = COALESCE(:active, active),
      password_hash = COALESCE(:password_hash, password_hash),
      pays_code = COALESCE(:pays_code, pays_code),
      email = COALESCE(:email, email)
    WHERE username = :username
    """
)


def _validate_role(role: str) -> str:
    normalized = role.upper()
    if normalized not in VALID_ROLES:
        raise HTTPException(status_code=400, detail="role invalide")
    return normalized


def _validate_username(username: str) -> None:
    if not username or len(username) > 100:
        raise HTTPException(status_code=400, detail="username invalide")


def _normalize_pays_code(pays_code: str | None) -> str | None:
    if not pays_code:
        return None
    normalized = pays_code.upper()
    if normalized not in VALID_PAYS:
        raise HTTPException(status_code=400, detail="pays_code invalide")
    return normalized


def _resolve_password_hash(password: str | None, password_hash: str | None) -> str:
    if password:
        if len(password) < 4:
            raise HTTPException(status_code=400, detail="password trop court")
        return hash_password(password)

    if not password_hash:
        raise HTTPException(status_code=400, detail="password requis")

    try:
        verify_password("test", password_hash)
    except Exception:
        raise HTTPException(status_code=400, detail="password_hash invalide")
    return password_hash


def _validate_optional_password_hash(password_hash: str) -> None:
    try:
        verify_password("test", password_hash)
    except Exception:
        raise HTTPException(status_code=400, detail="password_hash invalide")


@router.get("/")
async def list_users():
    async with SessionLocal() as session:
        res = await session.execute(LIST_SQL)
        return [dict(r) for r in res.mappings().all()]


@router.post(
    "/",
    responses={
        400: _USER_BAD_REQUEST,
        409: {"description": "Nom d'utilisateur déjà existant"},
    },
)
async def create_user(body: CreateUserRequest):
    role = _validate_role(body.role)
    _validate_username(body.username)
    pays_code = _normalize_pays_code(body.pays_code)
    password_hash = _resolve_password_hash(body.password, body.password_hash)

    async with SessionLocal() as session:
        try:
            await session.execute(
                INSERT_SQL,
                {
                    "username": body.username,
                    "password_hash": password_hash,
                    "role": role,
                    "pays_code": pays_code,
                    "email": body.email,
                },
            )
            await session.commit()
        except Exception:
            await session.rollback()
            raise HTTPException(status_code=409, detail="username déjà existant")

    return {"ok": True}


@router.patch(
    "/{username}",
    responses={
        400: _USER_BAD_REQUEST,
        404: {"description": "Utilisateur introuvable"},
    },
)
async def update_user(username: str, body: UpdateUserRequest):
    role = _validate_role(body.role) if body.role else None
    pays_code = _normalize_pays_code(body.pays_code)

    password_hash = body.password_hash
    if body.password is not None:
        password_hash = _resolve_password_hash(body.password, None)
    elif password_hash is not None:
        _validate_optional_password_hash(password_hash)

    async with SessionLocal() as session:
        res = await session.execute(
            UPDATE_SQL,
            {
                "username": username,
                "role": role,
                "active": body.active,
                "password_hash": password_hash,
                "pays_code": pays_code,
                "email": body.email,
            },
        )
        await session.commit()
        if res.rowcount == 0:
            raise HTTPException(status_code=404, detail="user introuvable")

    return {"ok": True}
