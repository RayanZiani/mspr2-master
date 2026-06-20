# IoT — ESP32 + DHT22

## Schéma de câblage

| DHT22 | ESP32 |
|---|---|
| VCC | 3.3V |
| GND | GND |
| DATA | GPIO 4 |

Le schéma visuel est dans `wiring/schema_cablage.png`.

## Flash du firmware (MicroPython)

```bash
# Installer esptool
pip install esptool

# Effacer la flash
esptool.py --port /dev/ttyUSB0 erase_flash

# Flasher MicroPython
esptool.py --port /dev/ttyUSB0 write_flash -z 0x1000 micropython.bin

# Uploader les fichiers firmware
mpremote cp firmware/config.py :config.py
mpremote cp firmware/sensor_dht.py :sensor_dht.py
mpremote cp firmware/mqtt_client.py :mqtt_client.py
mpremote cp firmware/main.py :main.py
```

## Simulateur (fallback démo)

Les pays **Équateur** et **Colombie** sont simulés via :

```bash
npm run sim:start:ec-co
```

## Capteur réel Brésil (ESP32)

- **Fréquence** : 1 relevé **toutes les 30 s** (`READ_INTERVAL` dans `firmware/config.py`)
- **Topic MQTT** : `futurekawa/bresil/entrepot_A/sensors` → mappe vers **Entrepôt BR-1** dans Aiven

```bash
npm run iot:up       # broker MQTT (port 1883)
npm run iot:bridge   # pont MQTT -> Aiven
```

Configurer `firmware/config.py` : WiFi + IP du PC (`MQTT_BROKER`).

Voir `docs/technique/mqtt_topics.md` pour le mapping complet.
