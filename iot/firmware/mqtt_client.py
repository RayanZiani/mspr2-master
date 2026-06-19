"""Client MQTT pour ESP32 (MicroPython) avec Last Will Testament."""
from umqtt.simple import MQTTClient
import ubinascii
import machine
import ujson


def get_client(broker: str, port: int, pays: str, entrepot: str) -> MQTTClient:
    """
    Crée et connecte un client MQTT avec LWT.
    Le LWT est publié automatiquement par le broker si l'ESP32 se déconnecte.
    """
    client_id = ubinascii.hexlify(machine.unique_id())
    status_topic = f"futurekawa/{pays}/{entrepot}/status"

    client = MQTTClient(client_id, broker, port=port, keepalive=60)

    # Last Will Testament : envoyé par le broker si l'ESP32 disparaît
    lwt_payload = ujson.dumps({"status": "offline", "source": "esp32", "pays": pays})
    client.set_last_will(status_topic, lwt_payload, retain=True, qos=1)

    client.connect()

    # Annonce de connexion réussie
    online_payload = ujson.dumps({"status": "online", "source": "esp32", "pays": pays})
    client.publish(status_topic, online_payload, retain=True, qos=1)

    return client
