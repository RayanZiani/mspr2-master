"""Vide les relevés température/humidité sur Aiven (table releve_capteur).

Conserve : pays, entrepôts, lots, capteurs, alertes.
Remet les lots actifs en statut CONFORME.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from aiven_mysql import connect_aiven


def main() -> int:
    cnx = connect_aiven(autocommit=False)
    cur = cnx.cursor()

    try:
        cur.execute("SELECT COUNT(*) FROM releve_capteur")
        before = cur.fetchone()[0]
        print(f"Relevés avant suppression : {before:,}")

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
        print(f"Supprimé : {deleted:,} relevé(s)")
        print(f"Lots remis CONFORME : {lots_reset}")
        print(f"Relevés restants : {after}")
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
