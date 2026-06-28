"""Tests unitaires pour le service webhook Discord siège."""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from conftest import load_siege_service, make_async_client_mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "siege"))

pytestmark = pytest.mark.unit


@pytest.fixture
def webhook():
    return load_siege_service("webhook_service")


class TestSiegeWebhook:
    async def test_post_embed_skipped_when_url_empty(self, webhook):
        with patch.object(webhook, "DISCORD_WEBHOOK_URL", ""):
            with patch("httpx.AsyncClient") as mock_cls:
                await webhook.send_discord("test", "bresil", "condition")
            mock_cls.assert_not_called()

    async def test_send_discord_posts_embed(self, webhook):
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_cm, mock_client = make_async_client_mock(mock_resp)

        with patch.object(webhook, "DISCORD_WEBHOOK_URL", "https://discord.example.com/hook"):
            with patch("httpx.AsyncClient", return_value=mock_cm):
                await webhook.send_discord("alerte test", "bresil", "condition")

        payload = mock_client.post.call_args[1]["json"]
        assert "embeds" in payload
        assert "BRESIL" in payload["embeds"][0]["title"]

    async def test_send_condition_alert_uses_rich_embed(self, webhook):
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_cm, mock_client = make_async_client_mock(mock_resp)

        with patch.object(webhook, "DISCORD_WEBHOOK_URL", "https://discord.example.com/hook"):
            with patch("httpx.AsyncClient", return_value=mock_cm):
                await webhook.send_condition_alert(
                    pays_slug="bresil",
                    pays_label="Brésil",
                    entrepot="Entrepot SP",
                    lot_id="lot-12345678",
                    temperature=35.0,
                    humidity=40.0,
                    temp_min=26.0,
                    temp_max=32.0,
                    hum_min=53.0,
                    hum_max=57.0,
                )

        payload = mock_client.post.call_args[1]["json"]
        assert "fields" in payload["embeds"][0]

    async def test_send_test_webhook_uses_production_on_render(self, webhook):
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_cm, mock_client = make_async_client_mock(mock_resp)

        with patch.object(webhook, "DISCORD_WEBHOOK_URL", "https://discord.example.com/hook"):
            with patch.dict("os.environ", {"RENDER": "true", "ENVIRONMENT": "local"}):
                with patch("httpx.AsyncClient", return_value=mock_cm):
                    await webhook.send_test_webhook(triggered_by="admin_siege")

        payload = mock_client.post.call_args[1]["json"]
        assert "production" in payload["embeds"][0]["fields"][1]["value"]

    async def test_http_error_is_swallowed(self, webhook):
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.text = "Internal Server Error"
        mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError(
            "500", request=MagicMock(), response=mock_resp
        )
        mock_cm, _ = make_async_client_mock(mock_resp)

        with patch.object(webhook, "DISCORD_WEBHOOK_URL", "https://discord.example.com/hook"):
            with patch("httpx.AsyncClient", return_value=mock_cm):
                await webhook.notify("test", "bresil", "condition")

    async def test_notify_delegates_to_send_discord(self, webhook):
        with patch.object(webhook, "send_discord", new_callable=AsyncMock) as mock_send:
            await webhook.notify("digest", "colombie", "peremption")
        mock_send.assert_called_once_with("digest", "colombie", "peremption")
