import sys
from pathlib import Path

import pytest
from fastapi import HTTPException

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "siege"))

pytestmark = pytest.mark.unit

from api.auth import (
    create_access_token,
    hash_password,
    require_role,
    require_user,
    verify_password,
)


def test_hash_and_verify_bcrypt_roundtrip():
    hashed = hash_password("Admin@2025!")
    assert hashed.startswith("$2b$")
    assert verify_password("Admin@2025!", hashed)
    assert not verify_password("wrong-password", hashed)


def test_verify_seed_style_bcrypt_hash():
    seed_hash = "$2b$12$hrcCoLHsdEnHTSB/pucd9.KWhPkmFOqB9f7R0vjHBiO0qq32eOp3a"
    assert verify_password("Admin@2025!", seed_hash)


def test_verify_pbkdf2_hash_path():
    from passlib.context import CryptContext
    pwd = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
    hashed = pwd.hash("legacy-password")
    assert verify_password("legacy-password", hashed)
    assert not verify_password("wrong", hashed)

    seed_hash = "$2b$12$hrcCoLHsdEnHTSB/pucd9.KWhPkmFOqB9f7R0vjHBiO0qq32eOp3a"
    assert not verify_password("not-the-password", seed_hash)


def test_create_access_token_roundtrip_via_require_user():
    token = create_access_token("admin_siege", "ADMIN", "SIEGE")
    user = require_user(token=token)
    assert user["sub"] == "admin_siege"
    assert user["role"] == "ADMIN"
    assert user["pays_code"] == "SIEGE"


def test_require_user_accepts_valid_token():
    token = create_access_token("resp_bresil", "USER", "BRESIL")
    user = require_user(token=token)
    assert user["sub"] == "resp_bresil"
    assert user["role"] == "USER"
    assert user["pays_code"] == "BRESIL"


def test_require_user_rejects_invalid_token():
    with pytest.raises(HTTPException) as exc:
        require_user(token="not.a.jwt")
    assert exc.value.status_code == 401


def test_require_user_rejects_token_without_role():
    from jose import jwt
    from api.auth import _algo, _secret

    token = jwt.encode({"sub": "ghost"}, _secret(), algorithm=_algo())
    with pytest.raises(HTTPException) as exc:
        require_user(token=token)
    assert exc.value.status_code == 401


def test_require_role_allows_matching_role():
    dep = require_role("ADMIN")
    user = dep(user={"sub": "admin", "role": "ADMIN", "pays_code": "SIEGE"})
    assert user["role"] == "ADMIN"


def test_require_role_denies_wrong_role():
    dep = require_role("ADMIN")
    with pytest.raises(HTTPException) as exc:
        dep(user={"sub": "user", "role": "USER", "pays_code": "SIEGE"})
    assert exc.value.status_code == 403
