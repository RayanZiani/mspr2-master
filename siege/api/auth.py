"""Authentification JWT et hachage des mots de passe."""

import os
from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
_pwd = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def _require_env(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise RuntimeError(f"Missing env var: {name}")
    return v


def _secret() -> str:
    return os.getenv("AUTH_JWT_SECRET", "dev-secret-change-me")


def _algo() -> str:
    return os.getenv("AUTH_JWT_ALG", "HS256")


def _access_ttl_minutes() -> int:
    return int(os.getenv("AUTH_ACCESS_TTL_MINUTES", "480"))


def verify_password(password: str, password_hash: str) -> bool:
    """Vérifie un mot de passe en clair contre son hash stocké."""
    if password_hash.startswith("$2"):
        try:
            return bcrypt.checkpw(
                password.encode("utf-8"),
                password_hash.encode("utf-8"),
            )
        except ValueError:
            return False
    return _pwd.verify(password, password_hash)


def hash_password(password: str) -> str:
    """Hache un mot de passe avec bcrypt."""
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(rounds=12),
    ).decode("utf-8")


def create_access_token(sub: str, role: str, pays_code: str | None) -> str:
    """Crée un JWT d'accès pour l'utilisateur authentifié."""
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=_access_ttl_minutes())
    payload = {
        "sub": sub,
        "role": role,
        "pays_code": pays_code,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    return jwt.encode(payload, _secret(), algorithm=_algo())


def require_user(token: str = Depends(_oauth2_scheme)) -> dict:
    """Dépendance FastAPI : extrait et valide l'utilisateur depuis le JWT."""
    try:
        payload = jwt.decode(token, _secret(), algorithms=[_algo()])
        sub = payload.get("sub")
        role = payload.get("role")
        pays_code = payload.get("pays_code")
        if not sub:
            raise HTTPException(status_code=401, detail="Token invalide")
        if not role:
            raise HTTPException(status_code=401, detail="Token invalide")
        return {"sub": sub, "role": role, "pays_code": pays_code}
    except JWTError as exc:
        raise HTTPException(
            status_code=401, detail="Token invalide ou expiré"
        ) from exc


def require_role(*roles: str):
    """Dépendance FastAPI : restreint l'accès aux rôles autorisés."""
    def _dep(user: dict = Depends(require_user)) -> dict:
        if user.get("role") not in roles:
            raise HTTPException(status_code=403, detail="Accès refusé")
        return user

    return _dep
