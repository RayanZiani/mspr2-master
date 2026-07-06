"""Authentification et profil utilisateur."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from api.auth import create_access_token, require_user, verify_password
from api.db.database import SessionLocal
from api.services.auth_service import get_user_account

router = APIRouter()

_INVALID_CREDENTIALS = "Identifiants invalides"

_LOGIN_RESPONSES = {
    401: {"description": _INVALID_CREDENTIALS},
}


class LoginRequest(BaseModel):
    """Identifiants de connexion."""

    username: str
    password: str


@router.post("/login", responses=_LOGIN_RESPONSES)
async def login(body: LoginRequest, request: Request):
    """Authentifie l'utilisateur et retourne un JWT."""
    user = await get_user_account(body.username)
    if not user or not user.get("active"):
        raise HTTPException(status_code=401, detail=_INVALID_CREDENTIALS)

    if not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail=_INVALID_CREDENTIALS)
    role = str(user.get("role") or "USER")
    ip = request.client.host if request.client else None
    try:
        async with SessionLocal() as session:
            await session.execute(
                text(
                    """
                    UPDATE user_account
                    SET last_login_at = UTC_TIMESTAMP(3),
                        last_login_ip = :ip
                    WHERE username = :username
                    """
                ),
                {"username": body.username, "ip": ip},
            )
            await session.commit()
    except SQLAlchemyError:
        pass
    return {
        "access_token": create_access_token(body.username, role, user.get("pays_code")),
        "token_type": "bearer",
        "role": role,
        "username": body.username,
        "pays_code": user.get("pays_code"),
        "email": user.get("email"),
    }


@router.get("/me")
async def me(user: Annotated[dict, Depends(require_user)]):
    """Retourne le profil de l'utilisateur connecté."""
    account = await get_user_account(user["sub"])
    return {
        "username": user["sub"],
        "role": user["role"],
        "pays_code": (account or {}).get("pays_code"),
        "email": (account or {}).get("email"),
    }
