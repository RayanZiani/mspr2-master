"""Tests unitaires pour le service de notifications webhook (Discord + Telegram)."""

import sys
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from conftest import COUNTRIES, load_webhook_service, make_async_client_mock

pytestmark = pytest.mark.unit

COUNTRY_LABELS = {
    "bresil": "BRESIL",
    "colombie": "COLOMBIE",
    "equateur": "EQUATEUR",
}


@pytest.fixture(params=COUNTRIES)
def ws(request):
    return load_webhook_service(request.param)


@pytest.fixture
def ws_bresil():
    return load_webhook_service("bresil")


# ─── Discord ────────────────────────────────────────────────────────────────


class TestSendDiscord:
    async def test_no_call_when_url_empty(self, ws):
        """Aucun appel HTTP si DISCORD_WEBHOOK_URL est vide."""
        with patch.object(ws, "DISCORD_WEBHOOK_URL", ""):
            with patch("httpx.AsyncClient") as mock_cls:
                await ws._send_discord("test", "bresil", "condition")
            mock_cls.assert_not_called()

    async def test_sends_embed_with_correct_title(self, ws):
        country = sys.modules["api.config"].PAYS
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_cm, mock_client = make_async_client_mock(mock_resp)

        with patch.object(ws, "DISCORD_WEBHOOK_URL", "https://discord.example.com/hook"):
            with patch("httpx.AsyncClient", return_value=mock_cm):
                await ws._send_discord("alerte test", country, "condition")

        payload = mock_client.post.call_args[1]["json"]
        assert "embeds" in payload
        assert payload["embeds"][0]["title"] == f"ALERTE FutureKawa — {COUNTRY_LABELS[country]}"

    async def test_condition_uses_red_color(self, ws):
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_cm, mock_client = make_async_client_mock(mock_resp)

        with patch.object(ws, "DISCORD_WEBHOOK_URL", "https://discord.example.com/hook"):
            with patch("httpx.AsyncClient", return_value=mock_cm):
                await ws._send_discord("temp hors seuil", "bresil", "condition")

        payload = mock_client.post.call_args[1]["json"]
        assert payload["embeds"][0]["color"] == 0xFF0000

    async def test_peremption_uses_orange_color(self, ws):
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_cm, mock_client = make_async_client_mock(mock_resp)

        with patch.object(ws, "DISCORD_WEBHOOK_URL", "https://discord.example.com/hook"):
            with patch("httpx.AsyncClient", return_value=mock_cm):
                await ws._send_discord("lot périmé", "bresil", "peremption")

        payload = mock_client.post.call_args[1]["json"]
        assert payload["embeds"][0]["color"] == 0xFF8C00

    async def test_connection_uses_yellow_color(self, ws):
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_cm, mock_client = make_async_client_mock(mock_resp)

        with patch.object(ws, "DISCORD_WEBHOOK_URL", "https://discord.example.com/hook"):
            with patch("httpx.AsyncClient", return_value=mock_cm):
                await ws._send_discord("capteur offline", "bresil", "connection")

        payload = mock_client.post.call_args[1]["json"]
        assert payload["embeds"][0]["color"] == 0xFFCC00

    async def test_http_error_is_swallowed(self, ws):
        """Une erreur HTTP ne doit pas propager d'exception au-delà du service."""
        mock_resp = MagicMock()
        mock_resp.status_code = 429
        mock_resp.text = "Too Many Requests"
        mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError(
            "429", request=MagicMock(), response=mock_resp
        )
        mock_cm, _ = make_async_client_mock(mock_resp)

        with patch.object(ws, "DISCORD_WEBHOOK_URL", "https://discord.example.com/hook"):
            with patch("httpx.AsyncClient", return_value=mock_cm):
                await ws._send_discord("test", "bresil", "condition")

    async def test_network_error_is_swallowed(self, ws):
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(side_effect=httpx.ConnectError("timeout"))
        mock_cm = MagicMock()
        mock_cm.__aenter__ = AsyncMock(return_value=mock_client)
        mock_cm.__aexit__ = AsyncMock(return_value=None)

        with patch.object(ws, "DISCORD_WEBHOOK_URL", "https://discord.example.com/hook"):
            with patch("httpx.AsyncClient", return_value=mock_cm):
                await ws._send_discord("test", "bresil", "condition")


# ─── Telegram ───────────────────────────────────────────────────────────────


class TestSendTelegram:
    async def test_no_call_when_token_empty(self, ws):
        with patch.object(ws, "TELEGRAM_BOT_TOKEN", ""):
            with patch("httpx.AsyncClient") as mock_cls:
                await ws._send_telegram("test", "bresil")
            mock_cls.assert_not_called()

    async def test_no_call_when_chat_id_empty(self, ws):
        with patch.object(ws, "TELEGRAM_BOT_TOKEN", "mytoken"):
            with patch.object(ws, "TELEGRAM_CHAT_ID", ""):
                with patch("httpx.AsyncClient") as mock_cls:
                    await ws._send_telegram("test", "bresil")
                mock_cls.assert_not_called()

    async def test_sends_html_message_to_correct_url(self, ws):
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_cm, mock_client = make_async_client_mock(mock_resp)

        with patch.object(ws, "TELEGRAM_BOT_TOKEN", "testtoken123"):
            with patch.object(ws, "TELEGRAM_CHAT_ID", "987654"):
                with patch("httpx.AsyncClient", return_value=mock_cm):
                    await ws._send_telegram("capteur offline", "bresil")

        mock_client.post.assert_called_once()
        url = mock_client.post.call_args[0][0]
        assert "testtoken123" in url
        assert "/sendMessage" in url

    async def test_payload_contains_chat_id_and_html(self, ws):
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_cm, mock_client = make_async_client_mock(mock_resp)

        with patch.object(ws, "TELEGRAM_BOT_TOKEN", "testtoken"):
            with patch.object(ws, "TELEGRAM_CHAT_ID", "111222"):
                with patch("httpx.AsyncClient", return_value=mock_cm):
                    await ws._send_telegram("message alerte", "equateur")

        payload = mock_client.post.call_args[1]["json"]
        assert payload["chat_id"] == "111222"
        assert payload["parse_mode"] == "HTML"
        assert "EQUATEUR" in payload["text"]
        assert "message alerte" in payload["text"]

    async def test_http_error_is_swallowed(self, ws):
        mock_resp = MagicMock()
        mock_resp.status_code = 400
        mock_resp.text = "Bad Request"
        mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError(
            "400", request=MagicMock(), response=mock_resp
        )
        mock_cm, _ = make_async_client_mock(mock_resp)

        with patch.object(ws, "TELEGRAM_BOT_TOKEN", "tok"):
            with patch.object(ws, "TELEGRAM_CHAT_ID", "123"):
                with patch("httpx.AsyncClient", return_value=mock_cm):
                    await ws._send_telegram("test", "bresil")


# ─── notify() ───────────────────────────────────────────────────────────────


class TestNotify:
    async def test_calls_both_channels(self, ws):
        """notify() doit appeler Discord ET Telegram."""
        discord_calls = []
        telegram_calls = []

        async def mock_discord(text, pays, alert_type):
            discord_calls.append((text, pays, alert_type))

        async def mock_telegram(text, pays):
            telegram_calls.append((text, pays))

        with patch.object(ws, "_send_discord", mock_discord):
            with patch.object(ws, "_send_telegram", mock_telegram):
                await ws.notify("alerte temp", "equateur", "condition")

        assert discord_calls == [("alerte temp", "equateur", "condition")]
        assert telegram_calls == [("alerte temp", "equateur")]

    async def test_telegram_failure_does_not_block_discord(self, ws):
        """return_exceptions=True garantit qu'une erreur Telegram n'annule pas Discord."""
        discord_calls = []

        async def mock_discord(text, pays, alert_type):
            discord_calls.append(True)

        async def mock_telegram_error(text, pays):
            raise RuntimeError("réseau indisponible")

        with patch.object(ws, "_send_discord", mock_discord):
            with patch.object(ws, "_send_telegram", mock_telegram_error):
                await ws.notify("test", "colombie", "connection")

        assert discord_calls, "Discord aurait dû être appelé malgré l'erreur Telegram"

    async def test_discord_failure_does_not_block_telegram(self, ws):
        telegram_calls = []

        async def mock_discord_error(text, pays, alert_type):
            raise RuntimeError("webhook discord invalide")

        async def mock_telegram(text, pays):
            telegram_calls.append(True)

        with patch.object(ws, "_send_discord", mock_discord_error):
            with patch.object(ws, "_send_telegram", mock_telegram):
                await ws.notify("test", "bresil", "peremption")

        assert telegram_calls, "Telegram aurait dû être appelé malgré l'erreur Discord"

    async def test_default_alert_type_is_condition(self, ws):
        discord_calls = []

        async def mock_discord(text, pays, alert_type):
            discord_calls.append(alert_type)

        with patch.object(ws, "_send_discord", mock_discord):
            with patch.object(ws, "_send_telegram", AsyncMock()):
                await ws.notify("test", "bresil")

        assert discord_calls == ["condition"]
