"""Vide les relevés température/humidité sur Aiven (table releve_capteur).

Conserve : pays, entrepôts, lots, capteurs, alertes.
Remet les lots actifs en statut CONFORME (pays ciblé ou tous).

Usage :
  python scripts/clear_releve_capteur_aiven.py           # tous pays
  python scripts/clear_releve_capteur_aiven.py --pays BR
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from aiven_mysql import connect_aiven

PAYS_ALIASES = {
    "BR": "BR",
    "BRESIL": "BR",
    "EC": "EC",
    "EQUATEUR": "EC",
    "CO": "CO",
    "COLOMBIE": "CO",
}


def _parse_pays(value: str | None) -> str | None:
    if not value:
        return None
    key = value.strip().upper()
    code = PAYS_ALIASES.get(key)
    if not code:
        raise SystemExit(f"Pays inconnu : {value}. Choix : BR, EC, CO")
    return code


def main() -> int:
    parser = argparse.ArgumentParser(description="Vide releve_capteur sur Aiven")
    parser.add_argument(
        "--pays",
        default=None,
        help="BR, EC ou CO — vide uniquement ce pays (défaut : tous)",
    )
    args = parser.parse_args()
    pays_code = _parse_pays(args.pays)

    cnx = connect_aiven(autocommit=False)
    cur = cnx.cursor()

    try:
        if pays_code:
            cur.execute(
                """
                SELECT COUNT(*)
                FROM releve_capteur r
                INNER JOIN capteur c ON c.id = r.capteur_id
                INNER JOIN entrepot e ON e.id = c.entrepot_id
                INNER JOIN pays p ON p.id = e.pays_id
                WHERE p.code = %s
                """,
                (pays_code,),
            )
            scope = f"pays {pays_code}"
        else:
            cur.execute("SELECT COUNT(*) FROM releve_capteur")
            scope = "tous pays"

        before = cur.fetchone()[0]
        print(f"Relevés avant suppression ({scope}) : {before:,}")

        if pays_code:
            cur.execute(
                """
                DELETE r FROM releve_capteur r
                INNER JOIN capteur c ON c.id = r.capteur_id
                INNER JOIN entrepot e ON e.id = c.entrepot_id
                INNER JOIN pays p ON p.id = e.pays_id
                WHERE p.code = %s
                """,
                (pays_code,),
            )
            deleted = cur.rowcount

            cur.execute(
                """
                UPDATE lot l
                INNER JOIN pays p ON p.id = l.pays_id
                SET l.statut = 'CONFORME'
                WHERE p.code = %s
                  AND l.sorti_le IS NULL
                  AND l.statut <> 'CONFORME'
                """,
                (pays_code,),
            )
            lots_reset = cur.rowcount

            cur.execute(
                """
                SELECT COUNT(*)
                FROM releve_capteur r
                INNER JOIN capteur c ON c.id = r.capteur_id
                INNER JOIN entrepot e ON e.id = c.entrepot_id
                INNER JOIN pays p ON p.id = e.pays_id
                WHERE p.code = %s
                """,
                (pays_code,),
            )
        else:
            cur.execute("DELETE FROM releve_capteur")
            deleted = cur.rowcount

            cur.execute(
                "UPDATE lot SET statut = 'CONFORME' "
                "WHERE sorti_le IS NULL AND statut <> 'CONFORME'"
            )
            lots_reset = cur.rowcount

            cur.execute("SELECT COUNT(*) FROM releve_capteur")

        after = cur.fetchone()[0]

        cnx.commit()
        print(f"Supprimé : {deleted:,} relevé(s) ({scope})")
        print(f"Lots remis CONFORME : {lots_reset}")
        print(f"Relevés restants ({scope}) : {after}")
        return 0
    except Exception as exc:
        cnx.rollback()
        print(f"ERREUR : {exc}", file=sys.stderr)
        return 1
    finally:
        cur.close()
        cnx.close()


if __name__ == "__main__":
    raise SystemExit(main())
