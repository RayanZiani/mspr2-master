import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "siege"))

pytestmark = pytest.mark.unit

from api.permissions import UserPermissions


@pytest.mark.parametrize("role,pays,expected", [
    ("SUPER_ADMIN", "SIEGE", True),
    ("ADMIN", "SIEGE", True),
    ("USER", "SIEGE", False),
    ("USER", "BRESIL", False),
])
def test_is_admin(role, pays, expected):
    perms = UserPermissions(role=role, pays_code=pays)
    assert perms.is_admin() is expected


@pytest.mark.parametrize("role,expected", [
    ("SUPER_ADMIN", True),
    ("ADMIN", False),
    ("USER", False),
])
def test_is_super_admin(role, expected):
    perms = UserPermissions(role=role, pays_code="SIEGE")
    assert perms.is_super_admin() is expected


@pytest.mark.parametrize("role,pays,expected", [
    ("USER", "SIEGE", True),
    ("ADMIN", "SIEGE", False),
    ("SUPER_ADMIN", "SIEGE", False),
    ("USER", "BRESIL", False),
])
def test_is_siege_user(role, pays, expected):
    perms = UserPermissions(role=role, pays_code=pays)
    assert perms.is_siege_user() is expected


@pytest.mark.parametrize("role,pays,can_write", [
    ("SUPER_ADMIN", "SIEGE", True),
    ("ADMIN", "SIEGE", True),
    ("USER", "SIEGE", False),
    ("USER", "BRESIL", True),
    ("USER", "EQUATEUR", True),
    ("USER", "COLOMBIE", True),
])
def test_can_write_lots(role, pays, can_write):
    perms = UserPermissions(role=role, pays_code=pays)
    assert perms.can_write_lots() is can_write


@pytest.mark.parametrize("role,pays,multi", [
    ("SUPER_ADMIN", "SIEGE", True),
    ("ADMIN", "SIEGE", True),
    ("USER", "SIEGE", True),
    ("USER", "BRESIL", False),
])
def test_can_view_multi_pays(role, pays, multi):
    perms = UserPermissions(role=role, pays_code=pays)
    assert perms.can_view_multi_pays() is multi


def test_allowed_pays_slugs_admin_sees_all():
    perms = UserPermissions.from_jwt_user({"role": "ADMIN", "pays_code": "SIEGE"})
    assert perms.allowed_pays_slugs() is None


def test_allowed_pays_slugs_country_user_restricted():
    perms = UserPermissions.from_jwt_user({"role": "USER", "pays_code": "BRESIL"})
    assert perms.allowed_pays_slugs() == {"bresil"}


def test_allowed_pays_slugs_unknown_country_empty():
    perms = UserPermissions.from_jwt_user({"role": "USER", "pays_code": "MARS"})
    assert perms.allowed_pays_slugs() == set()


@pytest.mark.parametrize("pays_code,email", [
    ("BRESIL", "resp.br@futurekawa.com"),
    ("EQUATEUR", "resp.eq@futurekawa.com"),
    ("COLOMBIE", "resp.co@futurekawa.com"),
    ("SIEGE", "admin@futurekawa.com"),
])
def test_alert_recipient_by_pays(pays_code, email):
    perms = UserPermissions(role="USER", pays_code=pays_code)
    assert perms.getAlertRecipientByPays(pays_code) == email


def test_only_super_admin_can_manage_users():
    assert UserPermissions(role="SUPER_ADMIN", pays_code="SIEGE").can_manage_users()
    assert not UserPermissions(role="ADMIN", pays_code="SIEGE").can_manage_users()
    assert not UserPermissions(role="USER", pays_code="SIEGE").can_manage_users()


def test_admin_and_super_admin_can_config_thresholds():
    assert UserPermissions(role="SUPER_ADMIN", pays_code="SIEGE").can_config_iot_thresholds()
    assert UserPermissions(role="ADMIN", pays_code="SIEGE").can_config_iot_thresholds()
    assert not UserPermissions(role="USER", pays_code="SIEGE").can_config_iot_thresholds()
