"""Connexion MySQL Aiven partagée par les scripts CLI."""

from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import mysql.connector
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[1]


def require_mysql_url() -> str:
    load_dotenv(REPO_ROOT / ".env")
    mysql_url = os.getenv("MYSQL_URL")
    if not mysql_url:
        raise SystemExit(
            "Variable MYSQL_URL manquante. Définis-la dans .env à la racine du projet."
        )
    return mysql_url


def parse_mysql_url(mysql_url: str) -> dict:
    parsed = urlparse(mysql_url)
    if parsed.scheme.lower() != "mysql":
        raise SystemExit("MYSQL_URL doit commencer par mysql://")

    database = (parsed.path or "").lstrip("/")
    if not database:
        raise SystemExit("MYSQL_URL doit contenir un nom de base (ex: /defaultdb)")

    query = parse_qs(parsed.query)
    ssl_mode = (query.get("ssl-mode", ["REQUIRED"])[0] or "REQUIRED").upper()

    return {
        "host": parsed.hostname,
        "port": parsed.port or 3306,
        "user": parsed.username,
        "password": parsed.password,
        "database": database,
        "ssl_mode": ssl_mode,
    }


def resolve_ca_path() -> str:
    ca_path = REPO_ROOT / "database" / "ca.pem"
    if ca_path.exists() and ca_path.is_dir():
        ca_path = ca_path / "ca.pem"
    if not ca_path.exists() or not ca_path.is_file() or ca_path.stat().st_size == 0:
        try:
            import certifi

            ca_path = Path(certifi.where())
        except Exception as exc:
            raise SystemExit(
                "Certificat manquant: database/ca.pem/ca.pem (et certifi indisponible)"
            ) from exc
    return str(ca_path)


def connect_aiven(*, autocommit: bool = False) -> mysql.connector.MySQLConnection:
    cfg = parse_mysql_url(require_mysql_url())
    ssl_disabled = cfg["ssl_mode"] in {"DISABLED", "DISABLE"}
    return mysql.connector.connect(
        host=cfg["host"],
        port=cfg["port"],
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
        autocommit=autocommit,
        use_pure=True,
        ssl_disabled=ssl_disabled,
        ssl_ca=None if ssl_disabled else resolve_ca_path(),
    )
