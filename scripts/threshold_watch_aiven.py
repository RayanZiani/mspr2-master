"""
Surveillance periodique des seuils IoT — lit le dernier releve Aiven et alerte Discord.

Complement du simulateur : utile quand les releves viennent d'ailleurs (ESP32, autre script)
ou pour re-verifier l'etat des lots toutes les N secondes.

Usage :
  python scripts/threshold_watch_aiven.py
  python scripts/threshold_watch_aiven.py --interval 60
"""

from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from aiven_mysql import connect_aiven
from threshold_alert import (
    ReleveCheckResult,
    print_alerts_console,
    print_scan_summary,
    process_releve,
)


def _fetch_latest_readings(cur) -> list[dict]:
    cur.execute(
        """
        SELECT r.capteur_id, r.temperature_c, r.humidite_pct, e.nom AS entrepot, p.code AS pays_code
        FROM releve_capteur r
        INNER JOIN (
            SELECT capteur_id, MAX(mesure_le) AS max_le
            FROM releve_capteur
            GROUP BY capteur_id
        ) latest ON latest.capteur_id = r.capteur_id AND latest.max_le = r.mesure_le
        INNER JOIN capteur c ON c.id = r.capteur_id AND c.active = 1
        INNER JOIN entrepot e ON e.id = c.entrepot_id
        INNER JOIN pays p ON p.id = e.pays_id
        ORDER BY p.code, e.nom
        """
    )
    return cur.fetchall()


def _scan_once() -> tuple[int, list[ReleveCheckResult]]:
    cnx = connect_aiven(autocommit=False)
    cur = cnx.cursor(dictionary=True)
    results: list[ReleveCheckResult] = []
    try:
        rows = _fetch_latest_readings(cur)
        if not rows:
            print("Aucun releve capteur - surveillance en attente.")
            return 0, results
        for row in rows:
            result = process_releve(
                cnx,
                str(row["capteur_id"]),
                float(row["temperature_c"]),
                float(row["humidite_pct"]),
            )
            if result is not None:
                results.append(result)
        return len(rows), results
    finally:
        cur.close()
        cnx.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Surveillance seuils capteurs -> Aiven + Discord")
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Intervalle entre deux verifications (defaut : 60 s)",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Une seule passe puis quitter",
    )
    args = parser.parse_args()

    if args.interval < 10:
        raise SystemExit("Intervalle minimum : 10 secondes")

    print(f"Surveillance seuils Aiven - intervalle {args.interval}s")
    print("Arret : Ctrl+C ou npm run sim:watch:stop\n")

    while True:
        stamp = datetime.now(timezone.utc).strftime("%H:%M:%S")
        try:
            count, results = _scan_once()
            print_scan_summary(stamp, count, results)
            print_alerts_console(results, stamp=f"{stamp} UTC")
        except KeyboardInterrupt:
            print("\nArret surveillance seuils.")
            return 0
        except Exception as exc:
            print(f"[{stamp} UTC] ERREUR : {exc}", file=sys.stderr)

        if args.once:
            return 0
        time.sleep(args.interval)


if __name__ == "__main__":
    raise SystemExit(main())
