"""Notifications webhook — Discord (siège / scripts Aiven)."""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx

from api.services.discord_embed import (
    build_condition_embed,
    build_message_embed,
    webhook_payload,
)

logger = logging.getLogger(__name__)

DISCORD_WEBHOOK_URL: str = os.getenv("DISCORD_WEBHOOK_URL", "")


async def _post_embed(payload: dict[str, Any], context: str) -> None:
    if not DISCORD_WEBHOOK_URL:
        logger.debug("DISCORD_WEBHOOK_URL non configure — notification ignoree")
        return
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.post(DISCORD_WEBHOOK_URL, json=payload)
            resp.raise_for_status()
            logger.info("Webhook Discord envoye (%s)", context)
        except httpx.HTTPStatusError as exc:
            logger.error(
                "Webhook Discord HTTP %s : %s",
                exc.response.status_code,
                exc.response.text[:200],
            )
        except httpx.HTTPError:
            logger.exception("Webhook Discord — erreur reseau (%s)", context)


async def send_discord(text: str, pays: str, alert_type: str = "condition") -> None:
    embed = build_message_embed(text, pays, alert_type)
    await _post_embed(webhook_payload(embed), f"{pays}/{alert_type}")


async def send_condition_alert(
    *,
    pays_slug: str,
    pays_label: str,
    entrepot: str,
    lot_id: str,
    temperature: float,
    humidity: float,
    temp_min: float,
    temp_max: float,
    hum_min: float,
    hum_max: float,
) -> None:
    embed = build_condition_embed(
        pays_slug=pays_slug,
        pays_label=pays_label,
        entrepot=entrepot,
        lot_id=lot_id,
        temperature=temperature,
        humidity=humidity,
        temp_min=temp_min,
        temp_max=temp_max,
        hum_min=hum_min,
        hum_max=hum_max,
    )
    await _post_embed(webhook_payload(embed), f"{pays_slug}/condition")


async def notify(text: str, pays: str, alert_type: str = "condition") -> None:
    await send_discord(text, pays, alert_type)
