"""MQTT subscriber — persists mesures to DB, alerts conditions/péremption, tracks capteur status."""

import asyncio
import json
import os
import threading
import time
import logging
from datetime import datetime, timezone

import paho.mqtt.client as mqtt
from sqlalchemy import select, update

from api.config import MQTT_BROKER_HOST, MQTT_BROKER_PORT, MQTT_TOPIC, PAYS, PEREMPTION_JOURS
from api.db.database import SessionLocal
from api.models.mesure import Mesure
from api.models.lot import Lot
from api.services.alert_service import check_alerts, is_lot_perime
from api.services.webhook_service import notify

logger = logging.getLogger(__name__)

# Délai (secondes) sans message avant de considérer un capteur déconnecté
CAPTEUR_TIMEOUT_SECONDS: int = int(os.getenv("CAPTEUR_TIMEOUT", "300"))

# Suivi en mémoire (thread-safe via GIL pour les dicts Python)
_last_seen: dict[str, datetime] = {}
_capteur_connected: dict[str, bool] = {}


def get_capteur_status() -> dict:
    """Retourne l'état de connexion de chaque entrepôt (appelé par la route /capteurs/status)."""
    now = datetime.now(timezone.utc)
    return {
        entrepot: {
            "connected": (now - last).total_seconds() <= CAPTEUR_TIMEOUT_SECONDS,
            "last_seen": last.isoformat(),
            "age_seconds": int((now - last).total_seconds()),
        }
        for entrepot, last in _last_seen.items()
    }


def _parse_timestamp(ts) -> datetime:
    """Accept ISO-8601 (simulator) or Unix epoch string (ESP32 firmware)."""
    if ts is None:
        return datetime.now(timezone.utc).replace(tzinfo=None)
    try:
        return datetime.fromisoformat(str(ts).replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        pass
    try:
        return datetime.fromtimestamp(float(ts), tz=timezone.utc).replace(tzinfo=None)
    except (ValueError, OSError):
        return datetime.now(timezone.utc).replace(tzinfo=None)


async def _resolve_lot_id(session, raw_lot_id: str | None, entrepot: str) -> str | None:
    """Return a valid lot id; fall back to the oldest active lot for this entrepot."""
    if raw_lot_id:
        row = await session.get(Lot, raw_lot_id)
        if row:
            return raw_lot_id
    result = await session.execute(
        select(Lot)
        .where(Lot.entrepot == entrepot)
        .order_by(Lot.date_stockage.asc())
        .limit(1)
    )
    lot = result.scalar_one_or_none()
    if lot:
        return lot.id
    logger.warning("No lot found for entrepot %s — mesure skipped", entrepot)
    return None


async def _persist(payload: dict, entrepot: str) -> None:
    """Enregistre une mesure et notifie uniquement sur changement de statut du lot."""
    temp = payload.get("temp")
    humidity = payload.get("humidity")
    if temp is None or humidity is None:
        return

    ts = _parse_timestamp(payload.get("timestamp"))

    async with SessionLocal() as session:
        lot_id = await _resolve_lot_id(session, payload.get("lot_id"), entrepot)
        if lot_id is None:
            return

        # Lire le statut actuel AVANT toute modification pour détecter les transitions
        lot_result = await session.execute(select(Lot).where(Lot.id == lot_id))
        lot = lot_result.scalar_one_or_none()
        current_statut = lot.statut if lot else "conforme"

        session.add(Mesure(
            lot_id=lot_id,
            timestamp=ts,
            temperature=temp,
            humidity=humidity,
        ))

        # — Vérification des conditions (température / humidité) —
        alerts = check_alerts(payload)
        if alerts:
            await session.execute(
                update(Lot).where(Lot.id == lot_id).values(statut="alerte")
            )
            if current_statut not in ("alerte", "perime"):
                # Première transition conforme → alerte : notification immédiate
                alert_text = "\n".join(alerts)
                notify_text = (
                    f"Lot {lot_id[:8]}… (entrepôt {entrepot}) → ALERTE\n{alert_text}"
                )
                logger.info("Statut lot %s : %s → alerte", lot_id, current_statut)
                await notify(notify_text, PAYS, alert_type="condition")

        # — Vérification péremption (lot > PEREMPTION_JOURS jours) —
        if lot and current_statut != "perime" and is_lot_perime(lot.date_stockage):
            await session.execute(
                update(Lot).where(Lot.id == lot_id).values(statut="perime")
            )
            perime_text = (
                f"Lot {lot_id[:8]}… (entrepôt {entrepot}) → PÉRIMÉ\n"
                f"Stocké depuis plus de {PEREMPTION_JOURS} jours — expédition prioritaire requise."
            )
            logger.warning("Statut lot %s : %s → périmé", lot_id, current_statut)
            await notify(perime_text, PAYS, alert_type="peremption")

        await session.commit()


def _handle_status_message(entrepot: str, payload: dict) -> None:
    """Traite un message de statut capteur (LWT online/offline du simulateur ou ESP32)."""
    status = payload.get("status", "")
    source = payload.get("source", "inconnu")

    if status == "online":
        was_connected = _capteur_connected.get(entrepot)
        _capteur_connected[entrepot] = True
        _last_seen[entrepot] = datetime.now(timezone.utc)
        if was_connected is False:
            msg = f"Capteur {entrepot} ({PAYS.upper()}) de nouveau en ligne ({source})."
            logger.info(msg)
            asyncio.run(notify(msg, PAYS, alert_type="connection"))

    elif status == "offline":
        was_connected = _capteur_connected.get(entrepot, True)
        _capteur_connected[entrepot] = False
        if was_connected:
            msg = (
                f"Capteur {entrepot} ({PAYS.upper()}) DECONNECTE ({source}) — "
                "vérification requise."
            )
            logger.warning(msg)
            asyncio.run(notify(msg, PAYS, alert_type="connection"))


def on_message(_client, _userdata, msg):
    """Traite un message MQTT : mesure capteur ou statut de connexion."""
    try:
        parts = msg.topic.split("/")
        # parts = ["futurekawa", pays, entrepot, type]
        if len(parts) < 4:
            return
        entrepot = parts[2]
        msg_type = parts[3]

        payload = json.loads(msg.payload.decode())

        if msg_type == "sensors":
            # Mise à jour du last_seen sur chaque mesure reçue
            _last_seen[entrepot] = datetime.now(timezone.utc)
            was_connected = _capteur_connected.get(entrepot)
            if was_connected is False:
                _capteur_connected[entrepot] = True
                reconnect_msg = f"Capteur {entrepot} ({PAYS.upper()}) de nouveau en ligne (données reçues)."
                logger.info(reconnect_msg)
                asyncio.run(notify(reconnect_msg, PAYS, alert_type="connection"))
            elif entrepot not in _capteur_connected:
                _capteur_connected[entrepot] = True
            asyncio.run(_persist(payload, entrepot))

        elif msg_type == "status":
            _handle_status_message(entrepot, payload)

    except (json.JSONDecodeError, UnicodeDecodeError, TypeError, ValueError, IndexError):
        logger.exception("Invalid MQTT payload on topic %s", msg.topic)
    except Exception:
        logger.exception("Failed to process MQTT message")


def _check_capteur_status() -> None:
    """Thread de surveillance : détecte les capteurs silencieux (timeout)."""
    while True:
        time.sleep(60)
        now = datetime.now(timezone.utc)
        for entrepot, last in list(_last_seen.items()):
            age = (now - last).total_seconds()
            is_connected = age <= CAPTEUR_TIMEOUT_SECONDS
            was_connected = _capteur_connected.get(entrepot, True)
            _capteur_connected[entrepot] = is_connected

            if was_connected and not is_connected:
                msg = (
                    f"Capteur {entrepot} ({PAYS.upper()}) HORS LIGNE — "
                    f"aucun relevé depuis {int(age / 60)} min."
                )
                logger.warning(msg)
                asyncio.run(notify(msg, PAYS, alert_type="connection"))
            elif not was_connected and is_connected:
                msg = f"Capteur {entrepot} ({PAYS.upper()}) de nouveau en ligne."
                logger.info(msg)
                asyncio.run(notify(msg, PAYS, alert_type="connection"))


def _run_loop():
    """Tente de se connecter au broker et relance en cas d'échec."""
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    client.on_message = on_message
    # Souscrire aux mesures ET aux statuts de connexion
    topics = [
        (MQTT_TOPIC, 0),
        (f"futurekawa/{PAYS}/+/status", 1),
    ]
    while True:
        try:
            logger.info("Connecting to MQTT %s:%s", MQTT_BROKER_HOST, MQTT_BROKER_PORT)
            client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT)
            for topic, qos in topics:
                client.subscribe(topic, qos)
                logger.info("Subscribed to %s (qos=%s)", topic, qos)
            client.loop_forever()
        except OSError:
            logger.exception("MQTT connection lost, retrying in 5s")
            time.sleep(5)


def start_mqtt():
    """Démarre le subscriber MQTT et le checker de statut dans des threads daemon."""
    threading.Thread(target=_run_loop, daemon=True, name="mqtt-subscriber").start()
    threading.Thread(target=_check_capteur_status, daemon=True, name="capteur-checker").start()
