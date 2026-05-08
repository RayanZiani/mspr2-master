import os
import sys
from pathlib import Path
from urllib.parse import urlparse, parse_qs

import mysql.connector
from dotenv import load_dotenv


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise SystemExit(f"Variable manquante: {name}")
    return value


def _read_sql(path: Path) -> str:
    if not path.exists():
        raise SystemExit(f"Fichier introuvable: {path}")
    return path.read_text(encoding="utf-8")


def _split_sql(sql: str) -> list[str]:
    statements: list[str] = []
    buf: list[str] = []

    in_sq = False
    in_dq = False
    in_bt = False
    in_line_comment = False
    in_block_comment = False

    i = 0
    n = len(sql)
    while i < n:
        ch = sql[i]
        nxt = sql[i + 1] if i + 1 < n else ""

        if in_line_comment:
            buf.append(ch)
            if ch == "\n":
                in_line_comment = False
            i += 1
            continue

        if in_block_comment:
            buf.append(ch)
            if ch == "*" and nxt == "/":
                buf.append(nxt)
                in_block_comment = False
                i += 2
            else:
                i += 1
            continue

        if not (in_sq or in_dq or in_bt):
            if ch == "-" and nxt == "-":
                in_line_comment = True
                buf.append(ch)
                buf.append(nxt)
                i += 2
                continue
            if ch == "/" and nxt == "*":
                in_block_comment = True
                buf.append(ch)
                buf.append(nxt)
                i += 2
                continue

        if ch == "'" and not (in_dq or in_bt):
            if in_sq and nxt == "'":
                buf.append(ch)
                buf.append(nxt)
                i += 2
                continue
            in_sq = not in_sq
            buf.append(ch)
            i += 1
            continue

        if ch == '"' and not (in_sq or in_bt):
            in_dq = not in_dq
            buf.append(ch)
            i += 1
            continue

        if ch == "`" and not (in_sq or in_dq):
            in_bt = not in_bt
            buf.append(ch)
            i += 1
            continue

        if ch == ";" and not (in_sq or in_dq or in_bt):
            stmt = "".join(buf).strip()
            if stmt:
                statements.append(stmt)
            buf = []
            i += 1
            continue

        buf.append(ch)
        i += 1

    tail = "".join(buf).strip()
    if tail:
        statements.append(tail)
    return statements


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

    ca_path = repo_root / "database" / "ca.pem"
    if not ca_path.exists():
        raise SystemExit("Certificat manquant: database/ca.pem")

    sql_path = repo_root / "database" / "seed_mysql.sql"
    sql = _read_sql(sql_path)

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
        ssl_ca=None if ssl_disabled else str(ca_path),
    )
    try:
        cur = cnx.cursor()
        for stmt in _split_sql(sql):
            cur.execute(stmt)
        cnx.commit()
        print("OK: seed appliqué.")
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

