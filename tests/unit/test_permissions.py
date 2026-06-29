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
    ("ADMIN", "BRESIL", True),
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
    ("ADMIN", "BRESIL", False),
    ("USER", "SIEGE", True),
    ("USER", "BRESIL", False),
])
def test_can_view_multi_pays(role, pays, multi):
    perms = UserPermissions(role=role, pays_code=pays)
    assert perms.can_view_multi_pays() is multi


def test_allowed_pays_slugs_admin_sees_all():
    perms = UserPermissions.from_jwt_user({"role": "ADMIN", "pays_code": "SIEGE"})
    assert perms.allowed_pays_slugs() is None


def test_allowed_pays_slugs_country_admin_restricted():
    perms = UserPermissions.from_jwt_user({"role": "ADMIN", "pays_code": "BRESIL"})
    assert perms.allowed_pays_slugs() == {"bresil"}


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
    assert perms.get_alert_recipient_by_pays(pays_code) == email


def test_only_super_admin_can_manage_users():
    assert UserPermissions(role="SUPER_ADMIN", pays_code="SIEGE").can_manage_users()
    assert not UserPermissions(role="ADMIN", pays_code="SIEGE").can_manage_users()
    assert not UserPermissions(role="USER", pays_code="SIEGE").can_manage_users()


@pytest.mark.parametrize("role,pays,allowed", [
    ("SUPER_ADMIN", "SIEGE", True),
    ("ADMIN", "SIEGE", False),
    ("ADMIN", "BRESIL", False),
    ("USER", "SIEGE", False),
])
def test_can_manage_global_webhook(role, pays, allowed):
    perms = UserPermissions(role=role, pays_code=pays)
    assert perms.can_manage_global_webhook() is allowed


@pytest.mark.parametrize("role,pays,can_config", [
    ("SUPER_ADMIN", "SIEGE", True),
    ("ADMIN", "SIEGE", True),
    ("ADMIN", "BRESIL", True),
    ("ADMIN", "EQUATEUR", True),
    ("USER", "SIEGE", False),
    ("USER", "BRESIL", False),
])
def test_can_config_iot_thresholds(role, pays, can_config):
    perms = UserPermissions(role=role, pays_code=pays)
    assert perms.can_config_iot_thresholds() is can_config


@pytest.mark.parametrize("role,pays,expected", [
    ("SUPER_ADMIN", "SIEGE", None),
    ("ADMIN", "SIEGE", None),
    ("ADMIN", "BRESIL", {"BR"}),
    ("ADMIN", "EQUATEUR", {"EC"}),
    ("ADMIN", "COLOMBIE", {"CO"}),
    ("USER", "BRESIL", set()),
])
def test_allowed_config_country_codes(role, pays, expected):
    perms = UserPermissions(role=role, pays_code=pays)
    result = perms.allowed_config_country_codes()
    assert result == expected


@pytest.mark.parametrize("role,pays,country,allowed", [
    ("ADMIN", "BRESIL", "BR", True),
    ("ADMIN", "BRESIL", "CO", False),
    ("ADMIN", "BRESIL", "EC", False),
    ("ADMIN", "SIEGE", "CO", True),
    ("SUPER_ADMIN", "SIEGE", "EC", True),
])
def test_can_config_iot_thresholds_for(role, pays, country, allowed):
    perms = UserPermissions(role=role, pays_code=pays)
    assert perms.can_config_iot_thresholds_for(country) is allowed


@pytest.mark.parametrize("role,pays,expected", [
    ("SUPER_ADMIN", "SIEGE", True),
    ("ADMIN", "SIEGE", True),
    ("ADMIN", "BRESIL", True),
    ("USER", "BRESIL", False),
])
def test_can_manage_entrepots(role, pays, expected):
    perms = UserPermissions(role=role, pays_code=pays)
    assert perms.can_manage_entrepots() is expected


@pytest.mark.parametrize("role,pays,expected", [
    ("SUPER_ADMIN", "SIEGE", True),
    ("ADMIN", "SIEGE", False),
    ("USER", "BRESIL", False),
])
def test_can_manage_exploitations(role, pays, expected):
    perms = UserPermissions(role=role, pays_code=pays)
    assert perms.can_manage_exploitations() is expected
