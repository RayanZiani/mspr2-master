import os
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
    ssl_mode = (qs.get("ssl-mode", [None])[0] or "").upper()

    return {
        "user": u.username,
        "password": u.password,
        "host": u.hostname,
        "port": u.port or 3306,
        "database": database,
        "ssl_disabled": ssl_mode == "",
    }


def _column_exists(cur, db: str, table: str, column: str) -> bool:
    cur.execute(
        """
        SELECT 1
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND COLUMN_NAME = %s
        LIMIT 1
        """,
        (db, table, column),
    )
    return cur.fetchone() is not None


def _exec(cur, sql: str):
    cur.execute(sql)


def main():
    load_dotenv()
    mysql_url = _require_env("MYSQL_URL")
    cfg = _parse_mysql_url(mysql_url)

    conn = mysql.connector.connect(
        user=cfg["user"],
        password=cfg["password"],
        host=cfg["host"],
        port=cfg["port"],
        database=cfg["database"],
        autocommit=False,
    )
    try:
        cur = conn.cursor()

        # Colonnes attendues pour la gestion utilisateurs "siège"
        if not _column_exists(cur, cfg["database"], "user_account", "pays_code"):
            _exec(
                cur,
                "ALTER TABLE user_account ADD COLUMN pays_code "
                "ENUM('SIEGE','BRESIL','EQUATEUR','COLOMBIE') NULL AFTER active",
            )

        if not _column_exists(cur, cfg["database"], "user_account", "email"):
            _exec(cur, "ALTER TABLE user_account ADD COLUMN email VARCHAR(255) NULL AFTER pays_code")

        if not _column_exists(cur, cfg["database"], "user_account", "last_login_at"):
            _exec(cur, "ALTER TABLE user_account ADD COLUMN last_login_at DATETIME(3) NULL AFTER email")

        if not _column_exists(cur, cfg["database"], "user_account", "last_login_ip"):
            _exec(cur, "ALTER TABLE user_account ADD COLUMN last_login_ip VARCHAR(45) NULL AFTER last_login_at")

        # Index utile pour filtrer par pays
        cur.execute("SHOW INDEX FROM user_account WHERE Key_name = 'idx_user_account_pays'")
        if cur.fetchone() is None:
            _exec(cur, "ALTER TABLE user_account ADD KEY idx_user_account_pays (pays_code)")

        conn.commit()
        print("OK: migration user_account appliquée")
    finally:
        conn.close()


if __name__ == "__main__":
    main()

