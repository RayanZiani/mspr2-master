"""Scheduleur de digest périodique — résumé FutureKawa toutes les 5 minutes."""

import asyncio
import logging
import os
import threading
import time

from sqlalchemy import select

from api.config import PAYS, PEREMPTION_JOURS
from api.db.database import SessionLocal
from api.models.lot import Lot
from api.services.mqtt_subscriber import get_capteur_status
from api.services.webhook_service import notify

logger = logging.getLogger(__name__)

DIGEST_INTERVAL_SECONDS: int = int(os.getenv("DIGEST_INTERVAL", "300"))


def _append_lot_section(lines: list[str], lots: list[Lot], header: str) -> None:
    if not lots:
        return
    lines.append(f"\n{header}")
    for lot in lots[:5]:
        lines.append(f"  - Lot {lot.id[:8]}... entrepot {lot.entrepot}")
    if len(lots) > 5:
        lines.append(f"  ... et {len(lots) - 5} autre(s)")


def _append_disconnected_section(
    lines: list[str], deconnectes: list[str], capteurs: dict
) -> None:
    if not deconnectes:
        return
    lines.append(f"\n{len(deconnectes)} capteur(s) HORS LIGNE :")
    for entrepot in deconnectes:
        age_min = capteurs[entrepot]["age_seconds"] // 60
        lines.append(f"  - {entrepot} : dernier signal il y a {age_min} min")


def _resolve_alert_type(alertes: list[Lot], perimes: list[Lot]) -> str:
    if perimes:
        return "peremption"
    if alertes:
        return "condition"
    return "connection"


async def _build_and_send_digest() -> None:
    """Interroge la BDD et envoie un résumé si des anomalies sont actives."""
    async with SessionLocal() as session:
        result = await session.execute(
            select(Lot)
            .where(Lot.statut != "conforme")
            .order_by(Lot.statut, Lot.date_stockage)
        )
        lots = result.scalars().all()

    alertes = [lot for lot in lots if lot.statut == "alerte"]
    perimes = [lot for lot in lots if lot.statut == "perime"]

    capteurs = get_capteur_status()
    deconnectes = [e for e, v in capteurs.items() if not v["connected"]]

    if not alertes and not perimes and not deconnectes:
        logger.debug("Digest : aucune anomalie active — notification ignorée")
        return

    lines = [f"Résumé FutureKawa — {PAYS.upper()}"]
    _append_lot_section(
        lines, alertes, f"{len(alertes)} lot(s) EN ALERTE (conditions hors seuil) :"
    )
    _append_lot_section(
        lines, perimes, f"{len(perimes)} lot(s) PERIMÉS (> {PEREMPTION_JOURS}j) :"
    )
    _append_disconnected_section(lines, deconnectes, capteurs)

    text = "\n".join(lines)
    await notify(text, PAYS, alert_type=_resolve_alert_type(alertes, perimes))
    logger.info(
        "Digest envoyé : %d en alerte, %d périmés, %d capteurs HS",
        len(alertes), len(perimes), len(deconnectes),
    )


def _digest_loop() -> None:
    """Boucle principale — envoie un digest toutes les DIGEST_INTERVAL secondes."""
    logger.info("Digest scheduler démarré (intervalle=%ds)", DIGEST_INTERVAL_SECONDS)
    while True:
        time.sleep(DIGEST_INTERVAL_SECONDS)
        try:
            asyncio.run(_build_and_send_digest())
        except Exception:
            logger.exception("Erreur lors de l'envoi du digest périodique")


def start_digest_scheduler() -> None:
    """Démarre le scheduleur de digest dans un thread daemon."""
    threading.Thread(target=_digest_loop, daemon=True, name="digest-scheduler").start()
