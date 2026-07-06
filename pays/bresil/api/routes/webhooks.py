"""Route de test des notifications webhook — Brésil."""

from fastapi import APIRouter
from pydantic import BaseModel

from api.config import PAYS
from api.services.webhook_service import (
    DISCORD_WEBHOOK_URL,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
    notify,
)

router = APIRouter()


class WebhookStatus(BaseModel):
    """État de configuration des webhooks Discord et Telegram."""

    discord_configured: bool
    telegram_configured: bool


class WebhookTestResult(BaseModel):
    """Résultat d'un envoi de notification de test."""

    pays: str
    discord_configured: bool
    telegram_configured: bool
    message: str


@router.get("/status", response_model=WebhookStatus)
async def webhook_status():
    """Indique quels canaux webhook sont configurés."""
    return WebhookStatus(
        discord_configured=bool(DISCORD_WEBHOOK_URL),
        telegram_configured=bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID),
    )


@router.post("/test", response_model=WebhookTestResult)
async def webhook_test():
    """Envoie une notification de test sur tous les canaux configurés."""
    text = (
        f"[TEST] Notification FutureKawa — {PAYS.upper()}\n"
        "Ceci est un message de test envoyé depuis l'API locale.\n"
        "Si vous recevez ce message, le canal est correctement configuré."
    )
    await notify(text, PAYS, alert_type="condition")
    return WebhookTestResult(
        pays=PAYS,
        discord_configured=bool(DISCORD_WEBHOOK_URL),
        telegram_configured=bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID),
        message="Notifications de test envoyées sur les canaux configurés.",
    )
