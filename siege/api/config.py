"""Configuration partagée de l'API siège FutureKawa."""

import os
import ssl
import tempfile
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from dotenv import load_dotenv

load_dotenv()


def _setup_ssl_certificate() -> str:
    """
    Configure le certificat SSL MySQL.
    Si MYSQL_SSL_CERT_CONTENT est défini, crée un fichier temporaire.
    Sinon, utilise le chemin défini dans MYSQL_SSL_CA.
    """
    cert_content = os.getenv("MYSQL_SSL_CERT_CONTENT")
    if cert_content:
        cert_path = Path(tempfile.gettempdir()) / "mysql-ca.pem"
        cert_path.write_text(cert_content)
        return str(cert_path)

    return os.getenv("MYSQL_SSL_CA", "/app/database/ca.pem")

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
REDIS_CACHE_TTL = int(os.getenv("REDIS_CACHE_TTL", "60"))
MESURES_DAYS = int(os.getenv("MESURES_DAYS", "30"))
MESURES_LIMIT = int(os.getenv("MESURES_LIMIT", "5000"))


def _api_url(env_var: str) -> str | None:
    """URL d'API pays — définie via .env / docker-compose.

    Sur Render, les APIs pays ne sont pas déployées : les données passent par MySQL.
    """
    url = (os.getenv(env_var) or "").strip()
    if url:
        return url
    if os.getenv("RENDER") or os.getenv("RENDER_EXTERNAL_URL"):
        return None
    raise RuntimeError(
        f"{env_var} requis — voir siege/.env.example "
        "ou ci-cd/Jenkinsfile (Préparation environnement)"
    )


API_URLS = {
    slug: url
    for slug, url in {
        "bresil": _api_url("API_BRESIL_URL"),
        "equateur": _api_url("API_EQUATEUR_URL"),
        "colombie": _api_url("API_COLOMBIE_URL"),
    }.items()
    if url
}

MYSQL_SSL_CA = _setup_ssl_certificate()


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
        if os.path.isfile(MYSQL_SSL_CA):
            ctx = ssl.create_default_context(cafile=MYSQL_SSL_CA)
        else:
            ctx = ssl.create_default_context()
        ctx.minimum_version = ssl.TLSVersion.TLSv1_2

        connect_args["ssl"] = ctx

    return async_url, connect_args


def get_database_config() -> tuple[str, dict]:
    """Retourne l'URL SQLAlchemy async et les connect_args MySQL."""
    mysql_url = os.getenv("MYSQL_URL") or os.getenv("DATABASE_URL")
    if not mysql_url:
        raise RuntimeError("MYSQL_URL (ou DATABASE_URL) requis pour l'API siège")
    return _parse_mysql_url(mysql_url)
