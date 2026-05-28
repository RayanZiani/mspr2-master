import os
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
_pwd = CryptContext(
    # Compat: on garde pbkdf2_sha256 pour les anciens comptes,
    # mais on privilégie bcrypt (coût ~12) pour les nouveaux.
    schemes=["bcrypt", "pbkdf2_sha256"],
    deprecated="auto",
)


def _require_env(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise RuntimeError(f"Missing env var: {name}")
    return v


def _secret() -> str:
    # Démo / dev: si non défini, on utilise une valeur par défaut explicite.
    # En prod, fournir une vraie valeur via env.
    return os.getenv("AUTH_JWT_SECRET", "dev-secret-change-me")


def _algo() -> str:
    return os.getenv("AUTH_JWT_ALG", "HS256")


def _access_ttl_minutes() -> int:
    return int(os.getenv("AUTH_ACCESS_TTL_MINUTES", "480"))  # 8h


def verify_password(password: str, password_hash: str) -> bool:
    return _pwd.verify(password, password_hash)


def hash_password(password: str) -> str:
    # Passlib choisit le premier schéma (bcrypt) par défaut.
    # On fixe explicitement le coût pour correspondre aux seeds.
    return _pwd.hash(password, rounds=12)


def create_access_token(sub: str, role: str, pays_code: str | None) -> str:
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
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalide ou expiré")


def require_role(*roles: str):
    def _dep(user: dict = Depends(require_user)) -> dict:
        if user.get("role") not in roles:
            raise HTTPException(status_code=403, detail="Accès refusé")
        return user

    return _dep

