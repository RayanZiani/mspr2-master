from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import text

from api.auth import hash_password, verify_password
from api.db.database import SessionLocal

router = APIRouter()


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


@router.get("/")
async def list_users():
    async with SessionLocal() as session:
        res = await session.execute(LIST_SQL)
        return [dict(r) for r in res.mappings().all()]


@router.post("/")
async def create_user(body: CreateUserRequest):
    role = body.role.upper()
    if role not in {"ADMIN", "USER"}:
        raise HTTPException(status_code=400, detail="role invalide")

    if not body.username or len(body.username) > 100:
        raise HTTPException(status_code=400, detail="username invalide")

    pays_code = body.pays_code.upper() if body.pays_code else None
    if pays_code and pays_code not in {"SIEGE", "BRESIL", "EQUATEUR", "COLOMBIE"}:
        raise HTTPException(status_code=400, detail="pays_code invalide")

    if not body.password and not body.password_hash:
        raise HTTPException(status_code=400, detail="password requis")

    if body.password and len(body.password) < 4:
        raise HTTPException(status_code=400, detail="password trop court")

    password_hash = None
    if body.password:
        password_hash = hash_password(body.password)
    else:
        # Validation légère: le hash doit être vérifiable par passlib.
        try:
            verify_password("test", body.password_hash or "")  # peut lever si format invalide
        except Exception:
            raise HTTPException(status_code=400, detail="password_hash invalide")
        password_hash = body.password_hash

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


@router.patch("/{username}")
async def update_user(username: str, body: UpdateUserRequest):
    role = body.role.upper() if body.role else None
    if role and role not in {"ADMIN", "USER"}:
        raise HTTPException(status_code=400, detail="role invalide")

    pays_code = body.pays_code.upper() if body.pays_code else None
    if pays_code and pays_code not in {"SIEGE", "BRESIL", "EQUATEUR", "COLOMBIE"}:
        raise HTTPException(status_code=400, detail="pays_code invalide")

    password_hash = body.password_hash
    if body.password is not None:
        if len(body.password) < 4:
            raise HTTPException(status_code=400, detail="password trop court")
        password_hash = hash_password(body.password)

    if password_hash is not None:
        try:
            verify_password("test", password_hash)
        except Exception:
            raise HTTPException(status_code=400, detail="password_hash invalide")

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

