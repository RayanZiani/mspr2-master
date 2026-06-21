"""
Maillon serie -> MQTT pour le vrai capteur ESP32 Bresil (COM3).

Le firmware iot/esp32.ino n'a pas de WiFi : il ecrit seulement sur le port
serie des trames texte :

    Temperature : 29.80 C
    Humidite    : 32.00 %
    ---

Ce script lit ces trames (robuste a la fragmentation serie) et les REPUBLIE en
MQTT sur le topic attendu par le pont officiel scripts/mqtt_bridge_bresil.py :

    futurekawa/bresil/entrepot_A/sensors   payload {"temp", "humidity", "timestamp"}

Le pont officiel se charge ensuite du mapping vers le capteur Aiven
(entrepot_A -> Entrepot BR-1 -> BR-SENSOR-01), de l'INSERT dans releve_capteur
et des alertes seuils. On ne duplique donc aucune logique metier.

Chaine complete :
    npm run iot:up        # broker MQTT (localhost:1883)
    npm run iot:bridge    # pont MQTT -> Aiven
    python iot/bridge/serial_to_mqtt.py --port COM3   # ce script

Dependances : pip install pyserial paho-mqtt
"""
import argparse
import json
import re
import sys
import time

import serial
import paho.mqtt.client as mqtt

FRAME_RE = re.compile(
    r"Temp\s*erature\s*:\s*([-\d.]+)\s*C.*?Humidite\s*:\s*([-\d.]+)\s*%",
    re.IGNORECASE | re.DOTALL,
)


def parse_args():
    ap = argparse.ArgumentParser(description="Pont serie -> MQTT (vrai capteur Bresil)")
    ap.add_argument("--port", required=True, help="Port serie, ex: COM3")
    ap.add_argument("--baud", type=int, default=115200)
    ap.add_argument("--entrepot", default="entrepot_A",
                    help="Slug entrepot du topic (entrepot_A -> BR-SENSOR-01)")
    ap.add_argument("--broker-host", default="localhost")
    ap.add_argument("--broker-port", type=int, default=1883)
    return ap.parse_args()


def main():
    args = parse_args()
    topic = f"futurekawa/bresil/{args.entrepot}/sensors"

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id="esp32-serial-bresil")
    print(f"[MQTT] connexion a {args.broker_host}:{args.broker_port} ...")
    client.connect(args.broker_host, args.broker_port, keepalive=60)
    client.loop_start()

    print(f"[SERIE] ouverture {args.port} @ {args.baud} ...")
    ser = serial.Serial(args.port, args.baud, timeout=1)
    print(f"[OK] pont actif -> topic {topic}. Ctrl+C pour arreter.\n")

    buffer = ""
    try:
        while True:
            chunk = ser.read(256)
            if not chunk:
                continue
            buffer += chunk.decode("utf-8", errors="ignore")

            last_end = 0
            for m in FRAME_RE.finditer(buffer):
                payload = {
                    "temp": float(m.group(1)),
                    "humidity": float(m.group(2)),
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                }
                client.publish(topic, json.dumps(payload))
                print(f"[PUBLIE] {topic} -> {payload}")
                last_end = m.end()

            if last_end:
                buffer = buffer[last_end:]
            if len(buffer) > 4096:
                buffer = buffer[-1024:]
    except KeyboardInterrupt:
        print("\n[STOP] arret demande.")
    finally:
        ser.close()
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    sys.exit(main())
