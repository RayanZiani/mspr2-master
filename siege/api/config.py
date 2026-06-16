import os
from urllib.parse import parse_qs, unquote, urlparse

from dotenv import load_dotenv

load_dotenv()

PAYS_SLUG = {
    "BR": "bresil",
    "EC": "equateur",
    "CO": "colombie",
}

STATUT_FRONT = {
    "CONFORME": "conforme",
    "ALERTE": "alerte",
    "PERIME": "perime",
    "EXPEDIE": "conforme",
}

REDIS_URL = os.getenv("REDIS_URL", "redis://redis-siege:6379")
REDIS_CACHE_TTL = int(os.getenv("REDIS_CACHE_TTL", 60))
MESURES_DAYS = int(os.getenv("MESURES_DAYS", 30))
MESURES_LIMIT = int(os.getenv("MESURES_LIMIT", 5000))

API_URLS = {
    "bresil": os.getenv("API_BRESIL_URL", "http://api-bresil:8000"),
    "equateur": os.getenv("API_EQUATEUR_URL", "http://api-equateur:8000"),
    "colombie": os.getenv("API_COLOMBIE_URL", "http://api-colombie:8000"),
}

MYSQL_SSL_CA = os.getenv("MYSQL_SSL_CA", "/app/database/ca.pem")


def _parse_mysql_url(mysql_url: str) -> tuple[str, dict]:
    u = urlparse(mysql_url)
    if u.scheme.lower() != "mysql":
        raise ValueError("MYSQL_URL doit commencer par mysql://")

    database = (u.path or "").lstrip("/")
    if not database:
        raise ValueError("MYSQL_URL doit contenir un nom de base")

    user = unquote(u.username or "")
    password = unquote(u.password or "")
    host = u.hostname or "localhost"
    port = u.port or 3306

    async_url = f"mysql+aiomysql://{user}:{password}@{host}:{port}/{database}"

    qs = parse_qs(u.query)
    ssl_mode = (qs.get("ssl-mode", ["REQUIRED"])[0] or "REQUIRED").upper()
    connect_args: dict = {}
    if ssl_mode not in {"DISABLED", "DISABLE"}:
        import ssl

        # Utilise le certificat personnalisé s'il existe, sinon utilise les certificats système par défaut
        if os.path.isfile(MYSQL_SSL_CA):
            ctx = ssl.create_default_context(cafile=MYSQL_SSL_CA)
        else:
            # Certificats système par défaut (pour Aiven, Render, etc.)
            ctx = ssl.create_default_context()
        
        connect_args["ssl"] = ctx

    return async_url, connect_args


def get_database_config() -> tuple[str, dict]:
    mysql_url = os.getenv("MYSQL_URL") or os.getenv("DATABASE_URL")
    if not mysql_url:
        raise RuntimeError("MYSQL_URL (ou DATABASE_URL) requis pour l'API siège")
    return _parse_mysql_url(mysql_url)
