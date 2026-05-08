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

```bash
python iot/simulator/simulate_sensor.py --pays bresil --entrepot entrepot_A
```
