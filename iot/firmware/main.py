import json
import time
import network
from firmware.config import WIFI_SSID, WIFI_PASSWORD, MQTT_BROKER, MQTT_PORT, MQTT_TOPIC, READ_INTERVAL
from firmware.mqtt_client import get_client
from firmware.sensor_dht import SensorDHT22


def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    while not wlan.isconnected():
        time.sleep(0.5)


def main():
    connect_wifi()
    sensor = SensorDHT22(pin=4)
    client = get_client(MQTT_BROKER, MQTT_PORT)

    while True:
        data = sensor.read()
        data["timestamp"] = str(time.time())
        client.publish(MQTT_TOPIC, json.dumps(data))
        time.sleep(READ_INTERVAL)


main()
