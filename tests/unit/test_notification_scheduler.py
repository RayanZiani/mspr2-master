"""Tests unitaires pour le scheduleur de digest périodique (pays)."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from conftest import COUNTRIES, load_pays_service

pytestmark = pytest.mark.unit


@pytest.fixture(params=COUNTRIES)
def scheduler(request):
    return load_pays_service(request.param, "notification_scheduler")


def _make_lot(lot_id: str, statut: str, entrepot: str = "ent-a"):
    lot = MagicMock()
    lot.id = lot_id
    lot.statut = statut
    lot.entrepot = entrepot
    return lot


class TestHelpers:
    def test_resolve_alert_type_peremption_priority(self, scheduler):
        alertes = [_make_lot("a", "alerte")]
        perimes = [_make_lot("b", "perime")]
        assert scheduler._resolve_alert_type(alertes, perimes) == "peremption"

    def test_resolve_alert_type_condition(self, scheduler):
        alertes = [_make_lot("a", "alerte")]
        assert scheduler._resolve_alert_type(alertes, []) == "condition"

    def test_resolve_alert_type_connection_only(self, scheduler):
        assert scheduler._resolve_alert_type([], []) == "connection"

    def test_append_lot_section_empty(self, scheduler):
        lines = ["header"]
        scheduler._append_lot_section(lines, [], "Alertes :")
        assert lines == ["header"]

    def test_append_lot_section_truncates_at_five(self, scheduler):
        lines = []
        lots = [_make_lot(f"lot-{i}", "alerte") for i in range(7)]
        scheduler._append_lot_section(lines, lots, "7 lots :")
        text = "\n".join(lines)
        assert "2 autre(s)" in text

    def test_append_disconnected_section(self, scheduler):
        lines = []
        capteurs = {"ent-a": {"age_seconds": 600, "connected": False}}
        scheduler._append_disconnected_section(lines, ["ent-a"], capteurs)
        assert "10 min" in "\n".join(lines)


class TestBuildAndSendDigest:
    @pytest.mark.asyncio
    async def test_no_anomaly_skips_notify(self, scheduler):
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_cm = MagicMock()
        mock_cm.__aenter__ = AsyncMock(return_value=mock_session)
        mock_cm.__aexit__ = AsyncMock(return_value=None)

        with patch.object(scheduler, "SessionLocal", return_value=mock_cm):
            with patch.object(scheduler, "get_capteur_status", return_value={}):
                with patch.object(scheduler, "notify", new_callable=AsyncMock) as mock_notify:
                    await scheduler._build_and_send_digest()
        mock_notify.assert_not_called()

    @pytest.mark.asyncio
    async def test_sends_digest_with_alerts(self, scheduler):
        lots = [_make_lot("lot-alert-1", "alerte")]
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = lots
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_cm = MagicMock()
        mock_cm.__aenter__ = AsyncMock(return_value=mock_session)
        mock_cm.__aexit__ = AsyncMock(return_value=None)

        with patch.object(scheduler, "SessionLocal", return_value=mock_cm):
            with patch.object(scheduler, "get_capteur_status", return_value={}):
                with patch.object(scheduler, "notify", new_callable=AsyncMock) as mock_notify:
                    await scheduler._build_and_send_digest()

        mock_notify.assert_called_once()
        call_args = mock_notify.call_args
        assert "EN ALERTE" in call_args[0][0]
        assert call_args[1]["alert_type"] == "condition"


@pytest.mark.parametrize("country", COUNTRIES)
def test_module_loads_for_each_country(country):
    mod = load_pays_service(country, "notification_scheduler")
    assert hasattr(mod, "_resolve_alert_type")
    assert hasattr(mod, "_build_and_send_digest")
