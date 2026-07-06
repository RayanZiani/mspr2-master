"""Tests unitaires pour auth_service (couche DB utilisateurs)."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from conftest import load_siege_service

pytestmark = pytest.mark.unit

USER_ROW = {
    "username": "admin_siege",
    "password_hash": "$2b$12$hash",
    "role": "ADMIN",
    "active": True,
    "pays_code": "SIEGE",
    "email": "admin@futurekawa.com",
}


@pytest.mark.asyncio
async def test_get_user_account_found():
    auth = load_siege_service("auth_service", mock_db=True)
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.mappings.return_value.first.return_value = USER_ROW
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_cm = MagicMock()
    mock_cm.__aenter__ = AsyncMock(return_value=mock_session)
    mock_cm.__aexit__ = AsyncMock(return_value=None)

    with patch.object(auth, "SessionLocal", return_value=mock_cm):
        user = await auth.get_user_account("admin_siege")

    assert user is not None
    assert user["username"] == "admin_siege"
    assert user["role"] == "ADMIN"


@pytest.mark.asyncio
async def test_get_user_account_not_found():
    auth = load_siege_service("auth_service", mock_db=True)
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.mappings.return_value.first.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_cm = MagicMock()
    mock_cm.__aenter__ = AsyncMock(return_value=mock_session)
    mock_cm.__aexit__ = AsyncMock(return_value=None)

    with patch.object(auth, "SessionLocal", return_value=mock_cm):
        user = await auth.get_user_account("unknown_user")

    assert user is None
