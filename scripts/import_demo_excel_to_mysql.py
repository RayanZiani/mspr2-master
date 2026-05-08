import os
import sys
from pathlib import Path
from urllib.parse import urlparse, parse_qs

import mysql.connector
import pandas as pd
from dotenv import load_dotenv


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise SystemExit(f"Variable manquante: {name}")
    return value


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


def _nan_to_none(df: pd.DataFrame) -> pd.DataFrame:
    return df.where(pd.notnull(df), None)


def _to_mysql_datetime_series(s: pd.Series) -> pd.Series:
    # accepte ISO avec 'Z' et renvoie des datetime naïfs (UTC)
    dt = pd.to_datetime(s, utc=True, errors="coerce")
    dt = dt.dt.tz_convert("UTC").dt.tz_localize(None)
    return dt


def _py_dt_or_none(v):
    if v is None or pd.isna(v):
        return None
    # pandas Timestamp -> python datetime
    if hasattr(v, "to_pydatetime"):
        return v.to_pydatetime()
    return v


def _py_int_or_none(v):
    if v is None or pd.isna(v):
        return None
    return int(v)


def _py_float_or_none(v):
    if v is None or pd.isna(v):
        return None
    return float(v)


def _exec_many(cur, sql: str, rows: list[tuple], batch: int = 2000) -> None:
    for i in range(0, len(rows), batch):
        cur.executemany(sql, rows[i : i + batch])


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    load_dotenv(repo_root / ".env")

    mysql_url = _require_env("MYSQL_URL")
    cfg = _parse_mysql_url(mysql_url)

    ca_path = repo_root / "database" / "ca.pem"
    if not ca_path.exists():
        raise SystemExit("Certificat manquant: database/ca.pem")

    xlsx_path = repo_root / "database" / "demo_data.xlsx"
    if not xlsx_path.exists():
        raise SystemExit("Fichier manquant: database/demo_data.xlsx")

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
        # Charge toutes les feuilles
        sheets = pd.read_excel(xlsx_path, sheet_name=None, engine="openpyxl")

        df_pays = _nan_to_none(sheets["pays"])
        df_exploitation = _nan_to_none(sheets["exploitation"])
        df_entrepot = _nan_to_none(sheets["entrepot"])
        df_lot = _nan_to_none(sheets["lot"])
        df_capteur = _nan_to_none(sheets["capteur"])
        df_releve = _nan_to_none(sheets["releve_capteur"])
        df_alerte = _nan_to_none(sheets["alerte"])

        # Normalisation dates
        for col in ["cree_le"]:
            df_exploitation[col] = _to_mysql_datetime_series(df_exploitation[col])
            df_entrepot[col] = _to_mysql_datetime_series(df_entrepot[col])
            df_capteur["installe_le"] = _to_mysql_datetime_series(df_capteur["installe_le"])
            df_lot["entre_le"] = _to_mysql_datetime_series(df_lot["entre_le"])
            df_lot["cree_le"] = _to_mysql_datetime_series(df_lot["cree_le"])

        if "sorti_le" in df_lot.columns:
            df_lot["sorti_le"] = _to_mysql_datetime_series(df_lot["sorti_le"])

        df_releve["mesure_le"] = _to_mysql_datetime_series(df_releve["mesure_le"])
        df_releve["cree_le"] = _to_mysql_datetime_series(df_releve["cree_le"])

        df_alerte["ouverte_le"] = _to_mysql_datetime_series(df_alerte["ouverte_le"])
        if "fermee_le" in df_alerte.columns:
            df_alerte["fermee_le"] = _to_mysql_datetime_series(df_alerte["fermee_le"])
        if "email_envoye_le" in df_alerte.columns:
            df_alerte["email_envoye_le"] = _to_mysql_datetime_series(df_alerte["email_envoye_le"])

        cur = cnx.cursor()

        # Nettoyage (ordre inverse des FK)
        print("Nettoyage des tables (DELETE)…")
        for table in ["alerte", "releve_capteur", "capteur", "lot", "entrepot", "exploitation", "pays"]:
            cur.execute(f"DELETE FROM {table}")

        print("Import pays…")
        pays_rows = [
            (
                _py_int_or_none(r.id),
                r.code,
                r.nom,
                _py_float_or_none(r.temperature_ideale_c),
                _py_float_or_none(r.humidite_ideale_pct),
                _py_float_or_none(r.tolerance_temperature_c),
                _py_float_or_none(r.tolerance_humidite_pct),
                r.email_responsable,
            )
            for r in df_pays.itertuples(index=False)
        ]
        _exec_many(
            cur,
            "INSERT INTO pays (id, code, nom, temperature_ideale_c, humidite_ideale_pct, tolerance_temperature_c, tolerance_humidite_pct, email_responsable) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
            pays_rows,
            batch=500,
        )

        print("Import exploitation…")
        exploitation_rows = [
            (_py_int_or_none(r.id), _py_int_or_none(r.pays_id), r.nom, _py_dt_or_none(r.cree_le))
            for r in df_exploitation.itertuples(index=False)
        ]
        _exec_many(
            cur,
            "INSERT INTO exploitation (id, pays_id, nom, cree_le) VALUES (%s,%s,%s,%s)",
            exploitation_rows,
            batch=500,
        )

        print("Import entrepot…")
        entrepot_rows = [
            (
                _py_int_or_none(r.id),
                _py_int_or_none(r.pays_id),
                _py_int_or_none(r.exploitation_id),
                r.nom,
                r.adresse,
                _py_dt_or_none(r.cree_le),
            )
            for r in df_entrepot.itertuples(index=False)
        ]
        _exec_many(
            cur,
            "INSERT INTO entrepot (id, pays_id, exploitation_id, nom, adresse, cree_le) VALUES (%s,%s,%s,%s,%s,%s)",
            entrepot_rows,
            batch=500,
        )

        print("Import lot…")
        lot_rows = [
            (
                r.id,
                _py_int_or_none(r.pays_id),
                _py_int_or_none(r.exploitation_id),
                _py_int_or_none(r.entrepot_id),
                _py_dt_or_none(r.entre_le),
                _py_dt_or_none(r.sorti_le),
                r.statut,
                _py_dt_or_none(r.cree_le),
            )
            for r in df_lot.itertuples(index=False)
        ]
        _exec_many(
            cur,
            "INSERT INTO lot (id, pays_id, exploitation_id, entrepot_id, entre_le, sorti_le, statut, cree_le) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
            lot_rows,
            batch=500,
        )

        print("Import capteur…")
        capteur_rows = [
            (
                r.id,
                _py_int_or_none(r.entrepot_id),
                r.numero_serie,
                r.modele,
                _py_dt_or_none(r.installe_le),
                _py_int_or_none(r.active),
            )
            for r in df_capteur.itertuples(index=False)
        ]
        _exec_many(
            cur,
            "INSERT INTO capteur (id, entrepot_id, numero_serie, modele, installe_le, active) VALUES (%s,%s,%s,%s,%s,%s)",
            capteur_rows,
            batch=500,
        )

        print(f"Import releve_capteur… ({len(df_releve):,} lignes)")
        releve_rows = [
            (
                _py_int_or_none(r.id),
                r.capteur_id,
                _py_dt_or_none(r.mesure_le),
                _py_float_or_none(r.temperature_c),
                _py_float_or_none(r.humidite_pct),
                _py_dt_or_none(r.cree_le),
            )
            for r in df_releve.itertuples(index=False)
        ]
        _exec_many(
            cur,
            "INSERT INTO releve_capteur (id, capteur_id, mesure_le, temperature_c, humidite_pct, cree_le) "
            "VALUES (%s,%s,%s,%s,%s,%s)",
            releve_rows,
            batch=2000,
        )

        print("Import alerte…")
        alerte_rows = [
            (
                _py_int_or_none(r.id),
                r.type,
                _py_int_or_none(r.pays_id),
                _py_int_or_none(r.entrepot_id),
                r.lot_id,
                _py_dt_or_none(r.ouverte_le),
                _py_dt_or_none(r.fermee_le),
                _py_dt_or_none(r.email_envoye_le),
                str(r.message) if r.message is not None else "",
            )
            for r in df_alerte.itertuples(index=False)
        ]
        _exec_many(
            cur,
            "INSERT INTO alerte (id, type, pays_id, entrepot_id, lot_id, ouverte_le, fermee_le, email_envoye_le, message) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            alerte_rows,
            batch=500,
        )

        cnx.commit()
        print("OK: import Excel -> MySQL terminé.")
        return 0
    except KeyError as e:
        cnx.rollback()
        print(f"Feuille manquante dans l'Excel: {e}", file=sys.stderr)
        return 1
    except mysql.connector.Error as e:
        cnx.rollback()
        print(f"ERREUR MySQL: {e}", file=sys.stderr)
        return 1
    finally:
        try:
            cnx.close()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())

