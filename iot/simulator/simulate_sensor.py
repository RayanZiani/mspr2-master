"""
Simulateur IoT — fallback si ESP32 défaillant en démo.
Usage: python simulate_sensor.py --pays bresil --entrepot entrepot_A
"""
import argparse
import json
import random
import time
import paho.mqtt.client as mqtt

SEUILS = {
    "bresil":   {"temp": 29, "humidity": 55},
    "equateur": {"temp": 31, "humidity": 60},
    "colombie": {"temp": 26, "humidity": 80},
}

parser = argparse.ArgumentParser()
parser.add_argument("--pays", required=True, choices=SEUILS.keys())
parser.add_argument("--entrepot", required=True)
parser.add_argument("--broker", default="localhost")
parser.add_argument("--port", type=int, default=1883)
parser.add_argument("--interval", type=int, default=5)
args = parser.parse_args()

topic = f"futurekawa/{args.pays}/{args.entrepot}/sensors"
seuil = SEUILS[args.pays]

client = mqtt.Client()
client.connect(args.broker, args.port)

print(f"Simulation démarrée — topic: {topic}")
while True:
    payload = {
        "temp": round(seuil["temp"] + random.uniform(-4, 4), 1),
        "humidity": round(seuil["humidity"] + random.uniform(-3, 3), 1),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "lot_id": "demo-lot-001",
    }
    client.publish(topic, json.dumps(payload))
    print(f"Publié : {payload}")
    time.sleep(args.interval)
