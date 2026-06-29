"""Configuration métier et connexions pour l'API FutureKawa — Brésil."""

import os
from urllib.parse import parse_qs, urlencode, urlsplit, urlunsplit

from dotenv import load_dotenv

load_dotenv()

PAYS = "bresil"

# Seuils de conditions spécifiques au Brésil
SEUIL_TEMP = 29.0       # °C
SEUIL_HUMIDITY = 55.0   # %
TOLERANCE_TEMP = 3.0    # ±3°C
TOLERANCE_HUMIDITY = 2.0  # ±2%
PEREMPTION_JOURS = 365

# Supporte une URL complète (ex: Aiven) via DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    if DATABASE_URL.startswith("mysql://") and not DATABASE_URL.startswith("mysql+aiomysql://"):
        DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+aiomysql://", 1)
    parts = urlsplit(DATABASE_URL)
    query_params = parse_qs(parts.query, keep_blank_values=True)
    if "ssl-mode" in query_params:
        query_params.pop("ssl-mode", None)
        query_string = urlencode(query_params, doseq=True)
        DATABASE_URL = urlunsplit(
            (parts.scheme, parts.netloc, parts.path, query_string, parts.fragment)
        )
else:
    DATABASE_URL = (
        f"mysql+aiomysql://{os.getenv('MYSQL_USER')}:"
        f"{os.getenv('MYSQL_PASSWORD')}@"
        f"{os.getenv('MYSQL_HOST', 'mysql-bresil')}:"
        f"{os.getenv('MYSQL_PORT', '3306')}/"
        f"{os.getenv('MYSQL_DATABASE')}"
    )

MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "mosquitto-bresil")
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", "1883"))
MQTT_TOPIC = f"futurekawa/{PAYS}/+/sensors"
