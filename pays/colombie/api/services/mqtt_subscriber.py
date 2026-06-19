"""MQTT subscriber — persists mesures to DB and updates lot statut on alert."""

import asyncio
import json
import threading
import time
import logging
from datetime import datetime, timezone

import paho.mqtt.client as mqtt
from sqlalchemy import select, update

from api.config import MQTT_BROKER_HOST, MQTT_BROKER_PORT, MQTT_TOPIC
from api.db.database import SessionLocal
from api.models.mesure import Mesure
from api.models.lot import Lot
from api.services.alert_service import check_alerts

logger = logging.getLogger(__name__)


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
    temp = payload.get("temp")
    humidity = payload.get("humidity")
    if temp is None or humidity is None:
        return

    ts = _parse_timestamp(payload.get("timestamp"))

    async with SessionLocal() as session:
        lot_id = await _resolve_lot_id(session, payload.get("lot_id"), entrepot)
        if lot_id is None:
            return

        session.add(Mesure(
            lot_id=lot_id,
            timestamp=ts,
            temperature=temp,
            humidity=humidity,
        ))

        alerts = check_alerts(payload)
        if alerts:
            await session.execute(
                update(Lot).where(Lot.id == lot_id).values(statut="alerte")
            )
            logger.info("Alertes pour lot %s : %s", lot_id, alerts)

        await session.commit()


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        entrepot = msg.topic.split("/")[2]
        asyncio.run(_persist(payload, entrepot))
    except Exception:
        logger.exception("Failed to process MQTT message")


def _run_loop():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    client.on_message = on_message
    while True:
        try:
            logger.info("Connecting to MQTT %s:%s", MQTT_BROKER_HOST, MQTT_BROKER_PORT)
            client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT)
            client.subscribe(MQTT_TOPIC)
            client.loop_forever()
        except Exception:
            logger.exception("MQTT connection lost, retrying in 5s")
            time.sleep(5)


def start_mqtt():
    thread = threading.Thread(target=_run_loop, daemon=True)
    thread.start()
