"""
Pont USB serie (firmware Arduino DHT) -> broker MQTT Brésil.

Lit COM5 (ou --port), parse Temperature/Humidite, publie sur le topic
attendu par mqtt_bridge_bresil.py -> Aiven -> dashboard.

Usage :
  npm run iot:up
  npm run iot:bridge          # terminal 1 : MQTT -> Aiven
  npm run iot:serial          # terminal 2 : COM -> MQTT
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt
import serial

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

TEMP_RE = re.compile(r"Temperature\s*:\s*([\d.]+)")
HUM_RE = re.compile(r"Humidite\s*:\s*([\d.]+)")


def _parse_line(line: str, pending: dict) -> dict | None:
    m = TEMP_RE.search(line)
    if m:
        pending["temp"] = float(m.group(1))
        return None
    m = HUM_RE.search(line)
    if m:
        pending["humidity"] = float(m.group(1))
    if "temp" in pending and "humidity" in pending:
        return dict(pending)
    return None


def run(port: str, baud: int, topic: str, broker: str, mqtt_port: int) -> None:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id="futurekawa-serial-br")
    client.connect(broker, mqtt_port, keepalive=60)
    client.loop_start()

    logger.info("Lecture %s @ %d -> %s (%s:%s)", port, baud, topic, broker, mqtt_port)

    pending: dict = {}
    with serial.Serial(port, baud, timeout=1) as ser:
        while True:
            try:
                raw = ser.readline()
                if not raw:
                    continue
                line = raw.decode("utf-8", errors="replace").strip()
                if not line or line == "---":
                    continue

                reading = _parse_line(line, pending)
                if reading is None:
                    continue

                payload = {
                    "temp": reading["temp"],
                    "humidity": reading["humidity"],
                    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                    "source": "serial",
                }
                client.publish(topic, json.dumps(payload), qos=0)
                logger.info(
                    "Publie MQTT | temp: %.1f C | hum: %.1f %%",
                    reading["temp"],
                    reading["humidity"],
                )
                pending.clear()
            except KeyboardInterrupt:
                logger.info("Arret du pont serie -> MQTT.")
                break
            except serial.SerialException as exc:
                logger.error("Port serie (%s) — retry 5s", exc)
                time.sleep(5)

    client.loop_stop()
    client.disconnect()


def main() -> None:
    parser = argparse.ArgumentParser(description="Pont COM -> MQTT Brésil")
    parser.add_argument("--port", default=os.getenv("SERIAL_PORT", "COM5"))
    parser.add_argument("--baud", type=int, default=int(os.getenv("SERIAL_BAUD", "115200")))
    parser.add_argument(
        "--topic",
        default=os.getenv("MQTT_TOPIC", "futurekawa/bresil/entrepot_A/sensors"),
    )
    parser.add_argument("--broker", default=os.getenv("MQTT_BROKER_HOST", "localhost"))
    parser.add_argument("--mqtt-port", type=int, default=int(os.getenv("MQTT_BROKER_PORT", "1883")))
    args = parser.parse_args()
    run(args.port, args.baud, args.topic, args.broker, args.mqtt_port)


if __name__ == "__main__":
    main()
