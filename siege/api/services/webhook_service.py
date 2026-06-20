"""Notifications webhook — Discord (siège / scripts Aiven)."""

from __future__ import annotations

import asyncio
import logging
import os

import httpx

logger = logging.getLogger(__name__)

DISCORD_WEBHOOK_URL: str = os.getenv("DISCORD_WEBHOOK_URL", "")

_DISCORD_COLORS = {
    "condition": 0xFF0000,
    "peremption": 0xFF8C00,
    "connection": 0xFFCC00,
}


async def send_discord(text: str, pays: str, alert_type: str = "condition") -> None:
    if not DISCORD_WEBHOOK_URL:
        logger.debug("DISCORD_WEBHOOK_URL non configure — notification ignoree")
        return
    color = _DISCORD_COLORS.get(alert_type, 0xFF0000)
    payload = {
        "embeds": [
            {
                "title": f"ALERTE FutureKawa — {pays.upper()}",
                "description": text,
                "color": color,
                "footer": {"text": "FutureKawa IoT Monitoring"},
            }
        ]
    }
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.post(DISCORD_WEBHOOK_URL, json=payload)
            resp.raise_for_status()
            logger.info("Webhook Discord envoye (%s / %s)", pays, alert_type)
        except httpx.HTTPStatusError as exc:
            logger.error(
                "Webhook Discord HTTP %s : %s",
                exc.response.status_code,
                exc.response.text[:200],
            )
        except httpx.HTTPError:
            logger.exception("Webhook Discord — erreur reseau (%s)", pays)


async def notify(text: str, pays: str, alert_type: str = "condition") -> None:
    await send_discord(text, pays, alert_type)
