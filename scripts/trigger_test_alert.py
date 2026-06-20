"""
Declenche volontairement une alerte temperature/humidite pour tester seuils + Discord.

Usage :
  python scripts/trigger_test_alert.py
  python scripts/trigger_test_alert.py --pays BR
  python scripts/trigger_test_alert.py --pays EC --offset 10
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from aiven_mysql import connect_aiven
from threshold_alert import print_alerts_console, process_releve


PAYS_ALIASES = {
    "BR": "BR",
    "BRESIL": "BR",
    "EC": "EC",
    "EQUATEUR": "EC",
    "CO": "CO",
    "COLOMBIE": "CO",
}


def _parse_pays(value: str) -> str:
    code = PAYS_ALIASES.get(value.strip().upper())
    if not code:
        raise SystemExit(f"Pays inconnu : {value}. Choix : BR, EC, CO")
    return code


def trigger(pays_code: str, offset: float, metric: str) -> int:
    cnx = connect_aiven(autocommit=False)
    cur = cnx.cursor(dictionary=True)
    try:
        cur.execute(
            """
            SELECT
                c.id AS capteur_id,
                c.numero_serie,
                e.nom AS entrepot,
                p.code,
                p.temperature_ideale_c,
                p.tolerance_temperature_c,
                p.humidite_ideale_pct,
                p.tolerance_humidite_pct
            FROM capteur c
            INNER JOIN entrepot e ON e.id = c.entrepot_id
            INNER JOIN pays p ON p.id = e.pays_id
            WHERE c.active = 1 AND p.code = %s
            ORDER BY e.nom
            LIMIT 1
            """,
            (pays_code,),
        )
        cap = cur.fetchone()
        if not cap:
            raise SystemExit(f"Aucun capteur actif pour {pays_code}")

        t_ideal = float(cap["temperature_ideale_c"])
        t_tol = float(cap["tolerance_temperature_c"])
        h_ideal = float(cap["humidite_ideale_pct"])
        h_tol = float(cap["tolerance_humidite_pct"])
        t_min, t_max = t_ideal - t_tol, t_ideal + t_tol
        h_min, h_max = h_ideal - h_tol, h_ideal + h_tol

        if metric == "temperature":
            temp_test = round(t_max + offset, 1)
            hum_test = round(h_ideal, 1)
        else:
            temp_test = round(t_ideal, 1)
            hum_test = round(h_max + offset, 1)

        cur.execute(
            """
            UPDATE lot l
            INNER JOIN entrepot e ON e.id = l.entrepot_id
            INNER JOIN pays p ON p.id = e.pays_id
            SET l.statut = 'CONFORME'
            WHERE p.code = %s AND l.sorti_le IS NULL
            """,
            (pays_code,),
        )
        cnx.commit()

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        cur.execute(
            """
            INSERT INTO releve_capteur (capteur_id, mesure_le, temperature_c, humidite_pct)
            VALUES (%s, %s, %s, %s)
            """,
            (cap["capteur_id"], now, temp_test, hum_test),
        )
        cnx.commit()

        print(f"Capteur  : {cap['numero_serie']} ({cap['entrepot']})")
        print(f"Seuils T : [{t_min:.1f} ; {t_max:.1f}] C")
        print(f"Seuils H : [{h_min:.1f} ; {h_max:.1f}] %")
        print(f"Releve injecte : {temp_test:.1f} C | {hum_test:.1f} %")
        print()

        result = process_releve(
            cnx,
            str(cap["capteur_id"]),
            temp_test,
            hum_test,
        )
        stamp = datetime.now(timezone.utc).strftime("%H:%M:%S")
        if result:
            print_alerts_console([result], stamp=f"{stamp} UTC")
        else:
            print("Aucune alerte declenchee (lot deja en ALERTE ou erreur).")
            print("Relancez avec un autre pays ou attendez sim:watch.")
        return 0
    finally:
        cur.close()
        cnx.close()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Injecte un releve hors seuil pour tester alertes BDD + Discord"
    )
    parser.add_argument("--pays", default="BR", help="BR, EC ou CO (defaut : BR)")
    parser.add_argument(
        "--offset",
        type=float,
        default=8.0,
        help="Ecart au-dela du seuil max (defaut : 8.0)",
    )
    parser.add_argument(
        "--metric",
        choices=("temperature", "humidity"),
        default="temperature",
        help="Grandeur hors seuil (defaut : temperature)",
    )
    args = parser.parse_args()
    pays = _parse_pays(args.pays)
    return trigger(pays, args.offset, args.metric)


if __name__ == "__main__":
    raise SystemExit(main())
