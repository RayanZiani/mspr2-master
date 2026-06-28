# IoT — ESP32 + DHT11 (connexion USB)

Prototype campus : l'ESP32 est branché au PC par **câble USB** (port série). Pas de WiFi sur le microcontrôleur.

## Schéma de câblage

| DHT11 | ESP32 |
|---|---|
| VCC | 3.3V |
| GND | GND |
| DATA | GPIO 4 |

Le schéma visuel est dans `wiring/schema_cablage.png`.

> Le cahier des charges prévoit un DHT22 en déploiement terrain. Sur campus, le matériel disponible est un **DHT11** (même câblage, précision moindre).

## Flash du firmware (Arduino)

1. Ouvrir `esp32.ino` dans l'Arduino IDE.
2. Installer la librairie **DHT sensor library** (Adafruit).
3. Sélectionner la carte ESP32 et le bon port COM.
4. Téléverser le sketch.

L'ESP32 envoie des trames texte sur le port série (115200 baud) :

```
Temperature : 29.80 C
Humidite    : 32.00 %
---
```

## Chaîne complète (capteur réel Brésil)

```
ESP32 + DHT11 (esp32.ino, ~20 s)
    │  USB / port série (ex. COM3)
    ▼
iot/bridge/serial_to_mqtt.py   (sur le PC)
    │  MQTT futurekawa/bresil/entrepot_A/sensors
    ▼
mosquitto local (npm run iot:up, port 1883)
    │
scripts/mqtt_bridge_bresil.py (npm run iot:bridge)
    │  map entrepot_A → Entrepôt BR-1 / BR-SENSOR-01
    ▼
releve_capteur (Aiven) → dashboard siège
```

### Terminaux

```bash
# T1 — broker MQTT
npm run iot:up

# T2 — pont MQTT → Aiven
npm run iot:bridge

# T3 — pont série → MQTT (adapter le port COM)
npm run iot:serial
# ou : python iot/bridge/serial_to_mqtt.py --port COM3

# T4 (optionnel) — simulateurs Équateur + Colombie (pas le BR)
npm run sim:start:ec-co
```

Dépendances du pont série : `pip install pyserial paho-mqtt`

## Simulateur (fallback démo)

Les pays **Équateur** et **Colombie** sont simulés via :

```bash
npm run sim:start:ec-co
```

Sans ESP32 branché : `npm run sim:start` simule les 6 capteurs (dont Brésil).

## Dossier `firmware/` (non utilisé)

Le répertoire `iot/firmware/` contient une **référence MicroPython + WiFi** (architecture cible en déploiement terrain). Il n'est **pas utilisé** dans le prototype campus filaire.

Voir `docs/technique/mqtt_topics.md` pour le mapping complet des topics.
