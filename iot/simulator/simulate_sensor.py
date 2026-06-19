"""
Simulateur IoT — fallback si ESP32 defaillant en demo.
Usage: python simulate_sensor.py --pays bresil --entrepot entrepot_A
       python simulate_sensor.py --pays bresil --entrepot entrepot_A --all --count 3
"""
import argparse
import json
import os
import random
import time
import paho.mqtt.client as mqtt

SEUILS = {
    "bresil":   {"temp": 29, "humidity": 55},
    "equateur": {"temp": 31, "humidity": 60},
    "colombie": {"temp": 26, "humidity": 80},
}

ENTREPOTS = {
    "bresil":   ["entrepot_A", "entrepot_B", "entrepot_C"],
    "equateur": ["entrepot_B", "entrepot_C"],
    "colombie": ["entrepot_C", "entrepot_D"],
}

parser = argparse.ArgumentParser()
parser.add_argument("--pays", required=True, choices=SEUILS.keys())
parser.add_argument("--entrepot", required=True)
parser.add_argument("--broker", default=os.getenv("MQTT_BROKER_HOST", "localhost"))
parser.add_argument("--port", type=int, default=int(os.getenv("MQTT_BROKER_PORT", 1883)))
parser.add_argument("--interval", type=int, default=int(os.getenv("SIMULATE_INTERVAL", 30)))
parser.add_argument("--all", action="store_true", help="Publie sur tous les entrepots du pays specifie")
parser.add_argument("--count", type=int, default=0, help="Nombre de cycles, 0 = infini")
args = parser.parse_args()


def publish_once(client: mqtt.Client, pays: str, entrepot: str) -> None:
    seuil = SEUILS[pays]
    payload = {
        "temp": round(seuil["temp"] + random.uniform(-4, 4), 1),
        "humidity": round(seuil["humidity"] + random.uniform(-3, 3), 1),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    topic = f"futurekawa/{pays}/{entrepot}/sensors"
    client.publish(topic, json.dumps(payload))
    print(f"Publie sur {topic} : {payload}")


def run_single_mode() -> None:
    client = mqtt.Client()
    client.connect(args.broker, args.port)
    print(f"Simulation demarre — {args.pays}/{args.entrepot} sur {args.broker}:{args.port}")
    cycles = 0
    while True:
        publish_once(client, args.pays, args.entrepot)
        cycles += 1
        if args.count and cycles >= args.count:
            break
        time.sleep(args.interval)


def run_all_mode() -> None:
    client = mqtt.Client()
    client.connect(args.broker, args.port)
    entrepots = ENTREPOTS[args.pays]
    print(f"Simulation demarre — {args.pays} tous entrepots sur {args.broker}:{args.port}")
    cycles = 0
    while True:
        for entrepot in entrepots:
            publish_once(client, args.pays, entrepot)
        cycles += 1
        if args.count and cycles >= args.count:
            break
        time.sleep(args.interval)


if args.all:
    run_all_mode()
else:
    run_single_mode()
