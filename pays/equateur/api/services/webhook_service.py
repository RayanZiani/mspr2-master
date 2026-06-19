"""Service de notification via webhooks — Discord et Telegram Bot."""

import asyncio
import logging
import os

import httpx

logger = logging.getLogger(__name__)

DISCORD_WEBHOOK_URL: str = os.getenv("DISCORD_WEBHOOK_URL", "")
TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")

_DISCORD_COLORS = {
    "condition": 0xFF0000,   # rouge — alerte température/humidité
    "peremption": 0xFF8C00,  # orange — lot trop ancien
    "connection": 0xFFCC00,  # jaune — capteur déconnecté / reconnecté
}


async def _send_discord(text: str, pays: str, alert_type: str) -> None:
    """Envoie un embed sur le webhook Discord configuré."""
    if not DISCORD_WEBHOOK_URL:
        logger.debug("DISCORD_WEBHOOK_URL non configuré — notification ignorée")
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
            logger.info("Webhook Discord envoyé (%s / %s)", pays, alert_type)
        except httpx.HTTPStatusError as exc:
            logger.error(
                "Webhook Discord — réponse HTTP %s : %s",
                exc.response.status_code,
                exc.response.text[:200],
            )
        except httpx.HTTPError:
            logger.exception("Webhook Discord — erreur réseau (%s)", pays)


async def _send_telegram(text: str, pays: str) -> None:
    """Envoie un message HTML via le Bot Telegram configuré."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.debug("TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID non configuré — notification ignorée")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": f"<b>ALERTE FutureKawa — {pays.upper()}</b>\n\n{text}",
        "parse_mode": "HTML",
    }
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            logger.info("Notification Telegram envoyée (%s)", pays)
        except httpx.HTTPStatusError as exc:
            logger.error(
                "Telegram — réponse HTTP %s : %s",
                exc.response.status_code,
                exc.response.text[:200],
            )
        except httpx.HTTPError:
            logger.exception("Telegram — erreur réseau (%s)", pays)


async def notify(text: str, pays: str, alert_type: str = "condition") -> None:
    """Notifie sur tous les canaux configurés (Discord + Telegram) en parallèle."""
    await asyncio.gather(
        _send_discord(text, pays, alert_type),
        _send_telegram(text, pays),
        return_exceptions=True,
    )
