import os
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import mysql.connector
from dotenv import load_dotenv


def _require_env(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise SystemExit(f"Variable manquante: {name}")
    return v


def _parse_mysql_url(mysql_url: str) -> dict:
    u = urlparse(mysql_url)
    if u.scheme.lower() != "mysql":
        raise SystemExit("MYSQL_URL doit commencer par mysql://")

    database = (u.path or "").lstrip("/")
    if not database:
        raise SystemExit("MYSQL_URL doit contenir un nom de base (ex: /defaultdb)")

    qs = parse_qs(u.query)
    ssl_mode = (qs.get("ssl-mode", ["REQUIRED"])[0] or "REQUIRED").upper()

    return {
        "host": u.hostname,
        "port": u.port or 3306,
        "user": u.username,
        "password": u.password,
        "database": database,
        "ssl_mode": ssl_mode,
    }


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    load_dotenv(repo_root / ".env")

    mysql_url = _require_env("MYSQL_URL")
    cfg = _parse_mysql_url(mysql_url)

    username = os.getenv("AUTH_USER_USERNAME") or os.getenv("AUTH_ADMIN_USER", "admin")
    password_hash = _require_env("AUTH_USER_PASSWORD_HASH") if os.getenv("AUTH_USER_PASSWORD_HASH") else _require_env("AUTH_ADMIN_PASSWORD_HASH")
    role = os.getenv("AUTH_USER_ROLE", "SUPER_ADMIN").upper()
    if role not in {"SUPER_ADMIN", "ADMIN", "USER"}:
        raise SystemExit("AUTH_USER_ROLE doit etre SUPER_ADMIN, ADMIN ou USER")

    ssl_disabled = cfg["ssl_mode"] in {"DISABLED", "DISABLE"}

    print(f"Connexion MySQL: {cfg['host']}:{cfg['port']} / {cfg['database']} (ssl-mode={cfg['ssl_mode']})")
    cnx = mysql.connector.connect(
        host=cfg["host"],
        port=cfg["port"],
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
        autocommit=False,
        use_pure=True,
        ssl_disabled=ssl_disabled,
    )

    try:
        cur = cnx.cursor()
        cur.execute(
            """
            INSERT INTO user_account (username, password_hash, role, active)
            VALUES (%s, %s, %s, 1)
            ON DUPLICATE KEY UPDATE
              password_hash = VALUES(password_hash),
              role = VALUES(role),
              active = 1
            """,
            (username, password_hash, role),
        )
        cnx.commit()
        print(f"OK: user_account upserted for '{username}' (role={role}).")
    except mysql.connector.Error as e:
        cnx.rollback()
        print(f"ERREUR MySQL: {e}", file=sys.stderr)
        return 1
    finally:
        try:
            cur.close()
        except Exception:
            pass
        cnx.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

