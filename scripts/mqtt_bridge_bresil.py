"""
Pont MQTT Brésil -> Aiven.

L'ESP32 publie toutes les 30 s sur :
  futurekawa/bresil/{entrepot}/sensors

Ce script ecoute le broker, mappe l'entrepot MQTT vers le capteur Excel Aiven
et INSERT dans releve_capteur.

Usage :
  npm run iot:up          # broker MQTT (terminal 1)
  npm run iot:bridge      # ce script (terminal 2)
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import paho.mqtt.client as mqtt

sys.path.insert(0, str(Path(__file__).resolve().parent))

from aiven_mysql import connect_aiven

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# Topic MQTT (firmware) -> entrepot Aiven (Excel demo)
ENTREPOT_SLUG_TO_NOM: dict[str, str] = {
    "entrepot_A": "Entrep\u00f4t BR-1",
}

PAYS_CODE = "BR"
TOPIC = "futurekawa/bresil/+/sensors"


def _load_capteur_ids() -> dict[str, str]:
    """Retourne {slug_mqtt: capteur_id uuid}."""
    cnx = connect_aiven()
    cur = cnx.cursor(dictionary=True)
    mapping: dict[str, str] = {}
    try:
        for slug, nom in ENTREPOT_SLUG_TO_NOM.items():
            cur.execute(
                """
                SELECT c.id AS capteur_id, e.nom AS entrepot_nom
                FROM capteur c
                INNER JOIN entrepot e ON e.id = c.entrepot_id
                INNER JOIN pays p ON p.id = e.pays_id
                WHERE p.code = %s AND e.nom = %s AND c.active = 1
                LIMIT 1
                """,
                (PAYS_CODE, nom),
            )
            row = cur.fetchone()
            if row:
                mapping[slug] = row["capteur_id"]
                logger.info(
                    "MQTT %s -> capteur %s (%s)",
                    slug,
                    row["capteur_id"][:8],
                    row["entrepot_nom"],
                )
            else:
                logger.warning("Capteur introuvable pour slug MQTT %s (%s)", slug, nom)
    finally:
        cur.close()
        cnx.close()

    if not mapping:
        raise SystemExit(
            "Aucun capteur BR mappe. Verifie l'import Excel (Entrepot BR-1)."
        )
    return mapping


def _parse_timestamp(raw) -> datetime:
    if raw is None:
        return datetime.now(timezone.utc).replace(tzinfo=None)
    try:
        return datetime.fromisoformat(str(raw).replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        pass
    try:
        return datetime.fromtimestamp(float(raw), tz=timezone.utc).replace(tzinfo=None)
    except (ValueError, OSError):
        return datetime.now(timezone.utc).replace(tzinfo=None)


def _insert_releve(capteur_id: str, temp: float, humidity: float, ts: datetime) -> None:
    cnx = connect_aiven(autocommit=False)
    cur = cnx.cursor()
    try:
        cur.execute(
            "INSERT INTO releve_capteur (capteur_id, mesure_le, temperature_c, humidite_pct) "
            "VALUES (%s, %s, %s, %s)",
            (capteur_id, ts, temp, humidity),
        )
        cnx.commit()
        from threshold_alert import process_releve

        process_releve(cnx, capteur_id, temp, humidity)
    except Exception:
        cnx.rollback()
        raise
    finally:
        cur.close()
        cnx.close()


def run() -> None:
    broker = os.getenv("MQTT_BROKER_HOST", "localhost")
    port = int(os.getenv("MQTT_BROKER_PORT", "1883"))
    capteur_map = _load_capteur_ids()

    def on_connect(client, _userdata, _flags, rc):
        if rc == 0:
            client.subscribe(TOPIC, qos=0)
            logger.info("Connecte au broker %s:%s — ecoute %s", broker, port, TOPIC)
        else:
            logger.error("Connexion MQTT refusee (code %s)", rc)

    def on_message(_client, _userdata, msg):
        try:
            parts = msg.topic.split("/")
            if len(parts) < 4:
                return
            slug = parts[2]
            capteur_id = capteur_map.get(slug)
            if not capteur_id:
                logger.warning("Topic %s : slug %s non mappe", msg.topic, slug)
                return

            payload = json.loads(msg.payload.decode())
            temp = payload.get("temp")
            humidity = payload.get("humidity")
            if temp is None or humidity is None:
                return

            ts = _parse_timestamp(payload.get("timestamp"))
            _insert_releve(capteur_id, float(temp), float(humidity), ts)
            logger.info(
                "[BR] %s | temp: %.1f C | hum: %.1f %% -> Aiven",
                slug,
                float(temp),
                float(humidity),
            )
        except Exception:
            logger.exception("Message MQTT invalide sur %s", msg.topic)

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id="futurekawa-bridge-bresil")
    client.on_connect = on_connect
    client.on_message = on_message

    while True:
        try:
            client.connect(broker, port, keepalive=60)
            client.loop_forever()
        except OSError as exc:
            logger.warning("Broker injoignable (%s) — retry 10s", exc)
            time.sleep(10)
        except KeyboardInterrupt:
            logger.info("Arret du pont MQTT Brésil.")
            break


if __name__ == "__main__":
    run()
