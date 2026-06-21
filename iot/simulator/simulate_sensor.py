"""
Simulateur IoT FutureKawa — publie température/humidité sur MQTT en continu.
Supporte le Last Will Testament (LWT) pour la détection de déconnexion.
Usage : lancé automatiquement par Docker Compose via les variables d'env.
"""
import json
import os
import random
import time
import logging

import paho.mqtt.client as mqtt

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

SEUILS = {
    "bresil":   {"temp": 29.0, "humidity": 55.0},
    "equateur": {"temp": 31.0, "humidity": 60.0},
    "colombie": {"temp": 26.0, "humidity": 80.0},
}

ENTREPOTS = {
    "bresil":   ["entrepot_A"],
    "equateur": ["entrepot_B", "entrepot_C"],
    "colombie": ["entrepot_C", "entrepot_D"],
}

PAYS             = os.getenv("PAYS", "bresil")
BROKER_HOST      = os.getenv("MQTT_BROKER_HOST", "localhost")
BROKER_PORT      = int(os.getenv("MQTT_BROKER_PORT", "1883"))
INTERVAL         = int(os.getenv("SIMULATE_INTERVAL", "30"))
CLIENT_ID        = f"simulator-{PAYS}"

STATUS_TOPIC_TPL = "futurekawa/{pays}/{entrepot}/status"
SENSOR_TOPIC_TPL = "futurekawa/{pays}/{entrepot}/sensors"


def _build_client() -> mqtt.Client:
    """Crée un client MQTT avec LWT configuré pour chaque entrepôt."""
    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION1,
        client_id=CLIENT_ID,
        clean_session=True,
    )

    # LWT sur le premier entrepôt (signal de déconnexion du simulateur)
    first_entrepot = ENTREPOTS[PAYS][0]
    lwt_topic = STATUS_TOPIC_TPL.format(pays=PAYS, entrepot=first_entrepot)
    lwt_payload = json.dumps({"status": "offline", "source": "simulator", "pays": PAYS})
    client.will_set(lwt_topic, lwt_payload, qos=1, retain=True)

    def on_connect(cli, _userdata, _flags, rc):
        if rc == 0:
            logger.info("Connecté au broker MQTT %s:%s", BROKER_HOST, BROKER_PORT)
            # Publier le statut "online" pour chaque entrepôt
            for entrepot in ENTREPOTS[PAYS]:
                topic = STATUS_TOPIC_TPL.format(pays=PAYS, entrepot=entrepot)
                payload = json.dumps({"status": "online", "source": "simulator", "pays": PAYS})
                cli.publish(topic, payload, qos=1, retain=True)
        else:
            logger.warning("Connexion MQTT refusée, code=%s", rc)

    def on_disconnect(_cli, _userdata, rc):
        if rc != 0:
            logger.warning("Déconnexion inattendue du broker MQTT (code=%s)", rc)

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    return client


def _publish_once(client: mqtt.Client, entrepot: str) -> None:
    """Publie une mesure simulée pour un entrepôt."""
    seuil = SEUILS[PAYS]
    payload = {
        "temp":      round(seuil["temp"] + random.uniform(-4, 4), 1),
        "humidity":  round(seuil["humidity"] + random.uniform(-3, 3), 1),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source":    "simulator",
    }
    topic = SENSOR_TOPIC_TPL.format(pays=PAYS, entrepot=entrepot)
    client.publish(topic, json.dumps(payload), qos=0)
    logger.info("Publié sur %s : temp=%.1f°C hum=%.1f%%", topic, payload["temp"], payload["humidity"])


def run() -> None:
    """Boucle principale : connexion avec retry + publication continue."""
    entrepots = ENTREPOTS.get(PAYS, [])
    if not entrepots:
        logger.error("Pays inconnu : %s. Choix valides : %s", PAYS, list(SEUILS.keys()))
        return

    logger.info("Simulateur démarré — pays=%s, entrepôts=%s, intervalle=%ss", PAYS, entrepots, INTERVAL)

    while True:
        client = _build_client()
        try:
            client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
            client.loop_start()

            while True:
                for entrepot in entrepots:
                    _publish_once(client, entrepot)
                time.sleep(INTERVAL)

        except OSError as exc:
            logger.warning("Impossible de joindre le broker (%s) — nouvelle tentative dans 10s", exc)
            time.sleep(10)
        except KeyboardInterrupt:
            logger.info("Arrêt du simulateur")
            # Publier "offline" proprement avant de quitter
            for entrepot in entrepots:
                topic = STATUS_TOPIC_TPL.format(pays=PAYS, entrepot=entrepot)
                payload = json.dumps({"status": "offline", "source": "simulator", "pays": PAYS})
                client.publish(topic, payload, qos=1, retain=True)
            client.loop_stop()
            client.disconnect()
            break
        except Exception:
            logger.exception("Erreur inattendue — nouvelle tentative dans 10s")
            time.sleep(10)
        finally:
            try:
                client.loop_stop()
                client.disconnect()
            except Exception:
                pass


if __name__ == "__main__":
    run()
