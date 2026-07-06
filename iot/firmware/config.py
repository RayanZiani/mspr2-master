# Reference MicroPython + WiFi — NON UTILISE en prototype campus (USB + esp32.ino).
# WiFi — a renseigner avant un deploiement terrain futur
WIFI_SSID = "NomDuReseau"
WIFI_PSK = ""

# Broker MQTT (IP du PC qui lance npm run iot:up, port 1883)
MQTT_BROKER = "192.168.1.100"
MQTT_PORT = 1883

# Identite capteur Brésil (topic MQTT, cf. docs/technique/mqtt_topics.md)
PAYS = "bresil"
ENTREPOT = "entrepot_A"  # entrepot_A -> Entrepot BR-1 dans Aiven (pont mqtt_bridge_bresil)
MQTT_TOPIC = f"futurekawa/{PAYS}/{ENTREPOT}/sensors"

# Frequence de releve capteur DHT22 (doc IoT + cahier des charges)
READ_INTERVAL = 30  # secondes entre chaque publication MQTT
