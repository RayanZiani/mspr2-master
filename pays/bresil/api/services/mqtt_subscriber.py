import json
import threading
import paho.mqtt.client as mqtt
from api.config import MQTT_BROKER_HOST, MQTT_BROKER_PORT, MQTT_TOPIC
from api.services.alert_service import check_alerts


def on_message(client, userdata, msg):
    payload = json.loads(msg.payload.decode())
    check_alerts(payload)


def start_mqtt():
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT)
    client.subscribe(MQTT_TOPIC)
    thread = threading.Thread(target=client.loop_forever, daemon=True)
    thread.start()
