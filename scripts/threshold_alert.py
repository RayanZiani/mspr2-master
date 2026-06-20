"""Evaluation seuils + alertes Discord (scripts sync Aiven)."""

from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.request
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

PAYS_SLUG = {"BR": "bresil", "EC": "equateur", "CO": "colombie"}


@dataclass(frozen=True)
class PaysSeuils:
    code: str
    slug: str
    pays_id: int
    entrepot_id: int
    entrepot_nom: str
    temp_min: float
    temp_max: float
    hum_min: float
    hum_max: float


def _load_context(cur, capteur_id: str) -> PaysSeuils | None:
    cur.execute(
        """
        SELECT
            p.id AS pays_id,
            p.code AS pays_code,
            p.temperature_ideale_c,
            p.tolerance_temperature_c,
            p.humidite_ideale_pct,
            p.tolerance_humidite_pct,
            e.id AS entrepot_id,
            e.nom AS entrepot_nom
        FROM capteur c
        INNER JOIN entrepot e ON e.id = c.entrepot_id
        INNER JOIN pays p ON p.id = e.pays_id
        WHERE c.id = %s
        LIMIT 1
        """,
        (capteur_id,),
    )
    row = cur.fetchone()
    if not row:
        return None
    code = str(row["pays_code"]).upper()
    t_ideal = float(row["temperature_ideale_c"])
    t_tol = float(row["tolerance_temperature_c"])
    h_ideal = float(row["humidite_ideale_pct"])
    h_tol = float(row["tolerance_humidite_pct"])
    return PaysSeuils(
        code=code,
        slug=PAYS_SLUG.get(code, code.lower()),
        pays_id=int(row["pays_id"]),
        entrepot_id=int(row["entrepot_id"]),
        entrepot_nom=str(row["entrepot_nom"]),
        temp_min=round(t_ideal - t_tol, 2),
        temp_max=round(t_ideal + t_tol, 2),
        hum_min=round(h_ideal - h_tol, 2),
        hum_max=round(h_ideal + h_tol, 2),
    )


def _check_reading(seuils: PaysSeuils, temperature: float, humidity: float) -> list[str]:
    messages: list[str] = []
    if temperature < seuils.temp_min or temperature > seuils.temp_max:
        messages.append(
            f"Temperature {temperature:.1f} C hors plage "
            f"[{seuils.temp_min:.1f} ; {seuils.temp_max:.1f}] C"
        )
    if humidity < seuils.hum_min or humidity > seuils.hum_max:
        messages.append(
            f"Humidite {humidity:.1f} % hors plage "
            f"[{seuils.hum_min:.1f} ; {seuils.hum_max:.1f}] %"
        )
    return messages


def _send_discord(text: str, pays: str) -> None:
    url = os.getenv("DISCORD_WEBHOOK_URL", "")
    if not url:
        logger.debug("DISCORD_WEBHOOK_URL absent — alerte Discord ignoree")
        return
    payload = {
        "embeds": [
            {
                "title": f"ALERTE FutureKawa — {pays.upper()}",
                "description": text,
                "color": 0xFF0000,
                "footer": {"text": "FutureKawa IoT Monitoring"},
            }
        ]
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10):
            logger.info("Alerte Discord envoyee (%s)", pays)
    except urllib.error.URLError as exc:
        logger.warning("Echec Discord : %s", exc)


def process_releve(cnx, capteur_id: str, temperature: float, humidity: float) -> None:
    """Verifie les seuils apres INSERT releve_capteur."""
    cur = cnx.cursor(dictionary=True)
    try:
        ctx = _load_context(cur, capteur_id)
        if not ctx:
            return

        alerts = _check_reading(ctx, temperature, humidity)

        cur.execute(
            """
            SELECT id, statut FROM lot
            WHERE entrepot_id = %s AND sorti_le IS NULL
            ORDER BY entre_le ASC
            LIMIT 1
            """,
            (ctx.entrepot_id,),
        )
        lot = cur.fetchone()
        if not lot:
            return

        lot_id = str(lot["id"])
        statut = str(lot["statut"] or "CONFORME").upper()

        if alerts:
            if statut != "CONFORME":
                return
            message = f"Lot {lot_id[:8]}… — {ctx.entrepot_nom}\n" + "\n".join(alerts)
            cur.execute(
                "UPDATE lot SET statut = 'ALERTE' WHERE id = %s",
                (lot_id,),
            )
            cur.execute(
                """
                INSERT INTO alerte (type, pays_id, entrepot_id, lot_id, message)
                VALUES ('CONDITION', %s, %s, %s, %s)
                """,
                (ctx.pays_id, ctx.entrepot_id, lot_id, message),
            )
            cnx.commit()
            print(f"\n!!! ALERTE {ctx.code} — {message}\n")
            _send_discord(message, ctx.slug)
        elif statut == "ALERTE":
            cur.execute(
                "UPDATE lot SET statut = 'CONFORME' WHERE id = %s",
                (lot_id,),
            )
            cnx.commit()
    except Exception:
        cnx.rollback()
        logger.exception("Erreur evaluation seuils capteur %s", capteur_id)
    finally:
        cur.close()
