import os

PAYS = "equateur"

# Seuils de conditions spécifiques à l'Équateur
SEUIL_TEMP = 31.0       # °C
SEUIL_HUMIDITY = 60.0   # %
TOLERANCE_TEMP = 3.0    # ±3°C
TOLERANCE_HUMIDITY = 2.0  # ±2%
PEREMPTION_JOURS = 365

DATABASE_URL = (
    f"mysql+aiomysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}"
    f"@{os.getenv('MYSQL_HOST', 'mysql-equateur')}:3306/{os.getenv('MYSQL_DATABASE')}"
)

MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "mosquitto-equateur")
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", 1883))
MQTT_TOPIC = f"futurekawa/{PAYS}/+/sensors"
