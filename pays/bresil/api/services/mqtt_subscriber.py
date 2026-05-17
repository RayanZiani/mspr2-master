"""Simple MQTT subscriber with automatic reconnect attempts.

This keeps behaviour identical but makes the subscriber more robust
when the broker is temporarily unreachable (useful for local dev).
"""

import json
import threading
import time
import logging
import paho.mqtt.client as mqtt
from api.config import MQTT_BROKER_HOST, MQTT_BROKER_PORT, MQTT_TOPIC
from api.services.alert_service import check_alerts

logger = logging.getLogger(__name__)


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        check_alerts(payload)
    except Exception:
        logger.exception("Failed to process MQTT message")


def _run_loop():
    """Try to connect and keep running; on failure, sleep and retry."""
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
