import os
from dotenv import load_dotenv
from urllib.parse import urlsplit, urlunsplit, parse_qs, urlencode

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
    # normalize scheme: if someone used mysql://, prefer aiomysql driver
    if DATABASE_URL.startswith("mysql://") and not DATABASE_URL.startswith("mysql+aiomysql://"):
        DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+aiomysql://", 1)
    # remove unsupported query params like ssl-mode that aiomysql will pass as kwargs
    parts = urlsplit(DATABASE_URL)
    qs = parse_qs(parts.query, keep_blank_values=True)
    if 'ssl-mode' in qs:
        qs.pop('ssl-mode', None)
        new_query = urlencode(qs, doseq=True)
        DATABASE_URL = urlunsplit((parts.scheme, parts.netloc, parts.path, new_query, parts.fragment))
else:
    DATABASE_URL = (
        f"mysql+aiomysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}"
        f"@{os.getenv('MYSQL_HOST', 'mysql-bresil')}:{os.getenv('MYSQL_PORT', '3306')}/{os.getenv('MYSQL_DATABASE')}"
    )

MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "mosquitto-bresil")
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", 1883))
MQTT_TOPIC = f"futurekawa/{PAYS}/+/sensors"
