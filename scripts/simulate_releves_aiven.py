"""
Simulateur de capteurs IoT — écrit directement dans Aiven (releve_capteur).

- Toutes les DISPLAY_INTERVAL secondes : affiche température / humidité (console), par pays.
- Toutes les INSERT_INTERVAL secondes : INSERT en base (1 relevé par capteur actif).

Usage :
  python scripts/simulate_releves_aiven.py
  python scripts/simulate_releves_aiven.py --pays EC
  python scripts/simulate_releves_aiven.py --interval 30
"""

from __future__ import annotations

import argparse
import random
import sys
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from aiven_mysql import connect_aiven


@dataclass
class CapteurSim:
    capteur_id: str
    numero_serie: str
    entrepot: str
    pays_code: str
    pays_nom: str
    temp_ideale: float
    hum_ideale: float
    temperature: float
    humidite: float


PAYS_ALIASES = {
    "BR": "BR",
    "BRESIL": "BR",
    "EC": "EC",
    "EQUATEUR": "EC",
    "CO": "CO",
    "COLOMBIE": "CO",
}


def _load_capteurs(
    pays_filter: str | None,
    exclude_pays: list[str] | None = None,
) -> list[CapteurSim]:
    cnx = connect_aiven()
    cur = cnx.cursor(dictionary=True)
    try:
        sql = """
            SELECT
                c.id AS capteur_id,
                c.numero_serie,
                e.nom AS entrepot,
                p.code AS pays_code,
                p.nom AS pays_nom,
                p.temperature_ideale_c AS temp_ideale,
                p.humidite_ideale_pct AS hum_ideale
            FROM capteur c
            INNER JOIN entrepot e ON e.id = c.entrepot_id
            INNER JOIN pays p ON p.id = e.pays_id
            WHERE c.active = 1
        """
        params: list = []
        if pays_filter:
            sql += " AND p.code = %s"
            params.append(pays_filter)
        if exclude_pays:
            placeholders = ", ".join(["%s"] * len(exclude_pays))
            sql += f" AND p.code NOT IN ({placeholders})"
            params.extend(exclude_pays)

        sql += " ORDER BY p.code, e.nom"
        cur.execute(sql, tuple(params))
        rows = cur.fetchall()
    finally:
        cur.close()
        cnx.close()

    if not rows:
        codes = pays_filter or "tous pays"
        raise SystemExit(
            f"Aucun capteur actif trouvé ({codes}). "
            "Importe d'abord database/demo_data.xlsx via scripts/import_demo_excel_to_mysql.py"
        )

    capteurs: list[CapteurSim] = []
    for row in rows:
        temp = float(row["temp_ideale"]) + random.uniform(-1.5, 1.5)
        hum = float(row["hum_ideale"]) + random.uniform(-1.0, 1.0)
        capteurs.append(
            CapteurSim(
                capteur_id=row["capteur_id"],
                numero_serie=row["numero_serie"],
                entrepot=row["entrepot"],
                pays_code=row["pays_code"],
                pays_nom=row["pays_nom"],
                temp_ideale=float(row["temp_ideale"]),
                hum_ideale=float(row["hum_ideale"]),
                temperature=round(temp, 1),
                humidite=round(max(0.0, min(100.0, hum)), 1),
            )
        )
    return capteurs


def _tick_values(capteur: CapteurSim) -> None:
    capteur.temperature = round(
        capteur.temperature + random.uniform(-0.4, 0.4), 1
    )
    capteur.humidite = round(
        max(0.0, min(100.0, capteur.humidite + random.uniform(-0.3, 0.3))), 1
    )


def _print_releve(capteur: CapteurSim) -> None:
    print(
        f"  {capteur.entrepot} ({capteur.numero_serie}) | "
        f"temp: {capteur.temperature:.1f} C | hum: {capteur.humidite:.1f} %"
    )


def _print_cycle(capteurs: list[CapteurSim]) -> None:
    by_pays: dict[str, list[CapteurSim]] = defaultdict(list)
    for capteur in capteurs:
        by_pays[capteur.pays_code].append(capteur)

    stamp = datetime.now(timezone.utc).strftime("%H:%M:%S")
    print(f"\n{'=' * 52}")
    print(f"  RELEVES SIMULES — {stamp} UTC")
    print(f"{'=' * 52}")

    for code in sorted(by_pays):
        group = by_pays[code]
        print(f"\n--- {group[0].pays_nom.upper()} ({code}) ---")
        for capteur in group:
            _tick_values(capteur)
            _print_releve(capteur)


def _insert_releves(capteurs: list[CapteurSim]) -> None:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    rows = [
        (c.capteur_id, now, c.temperature, c.humidite)
        for c in capteurs
    ]

    by_pays: dict[str, list[CapteurSim]] = defaultdict(list)
    for capteur in capteurs:
        by_pays[capteur.pays_code].append(capteur)

    cnx = connect_aiven(autocommit=False)
    cur = cnx.cursor()
    try:
        cur.executemany(
            "INSERT INTO releve_capteur (capteur_id, mesure_le, temperature_c, humidite_pct) "
            "VALUES (%s, %s, %s, %s)",
            rows,
        )
        cnx.commit()
        print(f"\n>>> INSERT Aiven @ {now.isoformat()}Z")
        print(f"    Total : {len(rows)} releve(s) = 1 par capteur actif")
        for code in sorted(by_pays):
            names = ", ".join(c.entrepot for c in by_pays[code])
            print(f"    {code} : {len(by_pays[code])} capteur(s) — {names}")
        print()
    except Exception as exc:
        cnx.rollback()
        print(f"ERREUR INSERT : {exc}", file=sys.stderr)
    finally:
        cur.close()
        cnx.close()


def _parse_pays(value: str | None) -> str | None:
    if not value or value.upper() == "ALL":
        return None
    key = value.strip().upper()
    code = PAYS_ALIASES.get(key)
    if not code:
        raise SystemExit(f"Pays inconnu : {value}. Choix : BR, EC, CO, ALL")
    return code


def main() -> int:
    parser = argparse.ArgumentParser(description="Simulateur capteurs → Aiven")
    parser.add_argument(
        "--pays",
        default="ALL",
        help="BR, EC, CO ou ALL (défaut : tous les capteurs actifs)",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=30,
        help="Cycle console + insertion BDD toutes les N secondes (defaut : 30)",
    )
    parser.add_argument(
        "--display-interval",
        type=int,
        default=None,
        help="(optionnel) affichage console, sinon = --interval",
    )
    parser.add_argument(
        "--insert-interval",
        type=int,
        default=None,
        help="(optionnel) insertion BDD, sinon = --interval",
    )
    parser.add_argument(
        "--exclude-pays",
        default="",
        help="Pays a ignorer (ex: BR quand ESP32 reel est branche). Ex: BR ou BR,EC",
    )
    args = parser.parse_args()

    display_interval = args.display_interval or args.interval
    insert_interval = args.insert_interval or args.interval

    if display_interval < 1 or insert_interval < display_interval:
        raise SystemExit("insert-interval doit etre >= display-interval >= 1")

    pays_code = _parse_pays(args.pays)
    exclude = [
        _parse_pays(p.strip()) or p.strip().upper()
        for p in args.exclude_pays.split(",")
        if p.strip()
    ]
    for code in exclude:
        if code not in {"BR", "EC", "CO"}:
            raise SystemExit(f"Pays exclude inconnu : {code}")

    capteurs = _load_capteurs(pays_code, exclude or None)

    print("Simulateur FutureKawa -> Aiven MySQL")
    print(
        f"Capteurs actifs : {len(capteurs)} "
        f"(2 entrepots x pays dans la BDD demo) | cycle : {display_interval}s"
    )
    if insert_interval == display_interval:
        print(f"Chaque cycle : affichage console + {len(capteurs)} INSERT (1 par capteur)")
    else:
        print(f"Affichage : {display_interval}s | insert : {insert_interval}s")
    print("Ctrl+C pour arreter.\n")

    ticks_per_insert = insert_interval // display_interval
    tick = 0

    try:
        while True:
            _print_cycle(capteurs)

            tick += 1
            if tick >= ticks_per_insert:
                _insert_releves(capteurs)
                tick = 0

            time.sleep(display_interval)
    except KeyboardInterrupt:
        print("\nArrêt du simulateur.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
