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

BROKERS = {
    "bresil": {"host": "localhost", "port": 1883, "entrepots": ["entrepot_A", "entrepot_B", "entrepot_C"]},
    "equateur": {"host": "localhost", "port": 1884, "entrepots": ["entrepot_B", "entrepot_C"]},
    "colombie": {"host": "localhost", "port": 1885, "entrepots": ["entrepot_C", "entrepot_D"]},
}

parser = argparse.ArgumentParser()
parser.add_argument("--pays", required=True, choices=SEUILS.keys())
parser.add_argument("--entrepot", required=True)
parser.add_argument("--broker", default="localhost")
parser.add_argument("--port", type=int, default=1883)
parser.add_argument("--interval", type=int, default=5)
parser.add_argument("--all", action="store_true", help="Publie des données sur les trois brokers et leurs entrepôts de démo")
parser.add_argument("--count", type=int, default=0, help="Nombre de cycles de publication avant arrêt, 0 = infini")
args = parser.parse_args()

def publish_once(client: mqtt.Client, pays: str, entrepot: str) -> dict:
    seuil = SEUILS[pays]
    payload = {
        "temp": round(seuil["temp"] + random.uniform(-4, 4), 1),
        "humidity": round(seuil["humidity"] + random.uniform(-3, 3), 1),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "lot_id": f"demo-{pays}-{entrepot}",
    }
    topic = f"futurekawa/{pays}/{entrepot}/sensors"
    client.publish(topic, json.dumps(payload))
    print(f"Publié sur {topic} : {payload}")
    return payload


def run_single_mode() -> None:
    topic = f"futurekawa/{args.pays}/{args.entrepot}/sensors"
    client = mqtt.Client()
    client.connect(args.broker, args.port)

    print(f"Simulation démarrée — topic: {topic}")
    cycles = 0
    while True:
        publish_once(client, args.pays, args.entrepot)
        cycles += 1
        if args.count and cycles >= args.count:
            break
        time.sleep(args.interval)


def run_all_mode() -> None:
    clients = {}
    for pays, config in BROKERS.items():
        client = mqtt.Client()
        client.connect(config["host"], config["port"])
        clients[pays] = client

    print("Simulation démo démarrée sur les trois brokers")
    cycles = 0
    while True:
        for pays, config in BROKERS.items():
            for entrepot in config["entrepots"]:
                publish_once(clients[pays], pays, entrepot)

        cycles += 1
        if args.count and cycles >= args.count:
            break
        time.sleep(args.interval)


if args.all:
    run_all_mode()
else:
    run_single_mode()
