"""Evaluation seuils + alertes Discord (scripts sync Aiven)."""

from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from discord_embed import build_condition_embed, webhook_payload
from email_alert import send_condition_email

REPO_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(REPO_ROOT / ".env")

logger = logging.getLogger(__name__)

PAYS_SLUG = {"BR": "bresil", "EC": "equateur", "CO": "colombie"}
PAYS_LABEL = {"BR": "Bresil", "EC": "Equateur", "CO": "Colombie"}


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


@dataclass(frozen=True)
class ReleveCheckResult:
    pays_code: str
    pays_label: str
    entrepot_nom: str
    lot_id: str
    temperature: float
    humidity: float
    temp_min: float
    temp_max: float
    hum_min: float
    hum_max: float
    violations: tuple[str, ...]
    new_alert: bool
    resolved: bool
    discord_sent: bool
    lot_statut: str

    @property
    def temp_ok(self) -> bool:
        return self.temp_min <= self.temperature <= self.temp_max

    @property
    def hum_ok(self) -> bool:
        return self.hum_min <= self.humidity <= self.hum_max


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


def _build_result(
    ctx: PaysSeuils,
    lot_id: str,
    temperature: float,
    humidity: float,
    violations: tuple[str, ...],
    *,
    new_alert: bool,
    resolved: bool,
    discord_sent: bool,
    lot_statut: str,
) -> ReleveCheckResult:
    return ReleveCheckResult(
        pays_code=ctx.code,
        pays_label=PAYS_LABEL.get(ctx.code, ctx.code),
        entrepot_nom=ctx.entrepot_nom,
        lot_id=lot_id,
        temperature=temperature,
        humidity=humidity,
        temp_min=ctx.temp_min,
        temp_max=ctx.temp_max,
        hum_min=ctx.hum_min,
        hum_max=ctx.hum_max,
        violations=violations,
        new_alert=new_alert,
        resolved=resolved,
        discord_sent=discord_sent,
        lot_statut=lot_statut,
    )


def _metric_line(label: str, value: float, unit: str, ok: bool, low: float, high: float) -> str:
    flag = "OK" if ok else "HORS SEUIL !"
    return (
        f"  {label:<8} {value:5.1f} {unit:<2}  "
        f"(seuil {low:.1f} - {high:.1f} {unit})  [{flag}]"
    )


def _print_one_alert(result: ReleveCheckResult) -> None:
    if result.resolved:
        tag = "RETOUR CONFORME"
    elif result.new_alert:
        tag = "NOUVELLE ALERTE"
    else:
        tag = "ALERTE ACTIVE"

    print(f"\n  --- {tag} : {result.pays_label.upper()} ({result.pays_code}) ---")
    print(f"  Entrepot : {result.entrepot_nom}")
    if result.lot_id:
        print(f"  Lot      : {result.lot_id[:8]}...")
    print(
        f"  Mesure   : {result.temperature:.1f} C  |  {result.humidity:.1f} %"
    )
    print(_metric_line("Temp.", result.temperature, "C", result.temp_ok, result.temp_min, result.temp_max))
    print(_metric_line("Humid.", result.humidity, "%", result.hum_ok, result.hum_min, result.hum_max))

    if result.resolved:
        print("  Action   : lot repasse en CONFORME")
    elif result.new_alert:
        discord = "Discord envoye OK" if result.discord_sent else "Discord ECHEC (verifier URL)"
        print(f"  Action   : alerte BDD + {discord}")
    else:
        print(f"  Statut   : lot deja en {result.lot_statut}")


def _print_active_compact(result: ReleveCheckResult) -> None:
    t_flag = "OK" if result.temp_ok else "HORS SEUIL"
    h_flag = "OK" if result.hum_ok else "HORS SEUIL"
    print(
        f"  >> {result.pays_code} {result.entrepot_nom} | "
        f"T={result.temperature:.1f}C [{result.temp_min:.0f}-{result.temp_max:.0f}] {t_flag} | "
        f"H={result.humidity:.1f}% [{result.hum_min:.0f}-{result.hum_max:.0f}] {h_flag} | "
        f"lot {result.lot_statut}"
    )


def print_alerts_console(
    results: list[ReleveCheckResult],
    stamp: str | None = None,
) -> None:
    """Affiche un bloc d'alertes formate (simulateur + surveillance)."""
    notable = [r for r in results if r.new_alert or r.resolved]
    active = [r for r in results if r.violations and not r.new_alert]

    if not notable and not active:
        return

    width = 52

    if notable:
        print()
        print("=" * width)
        title = "  ALERTES SEUILS IoT"
        if stamp:
            title += f" - {stamp}"
        print(title)
        print(f"  {len(notable)} evenement(s)")
        print("=" * width)
        for result in notable:
            _print_one_alert(result)
        print()
        print("=" * width)

    if active:
        print()
        print(f"  Hors seuil en cours ({len(active)}) :")
        for result in active:
            _print_active_compact(result)


def print_scan_summary(
    stamp: str,
    sensor_count: int,
    results: list[ReleveCheckResult],
) -> None:
    """Ligne de synthese apres chaque cycle de surveillance."""
    active = sum(1 for r in results if r.violations and not r.new_alert)
    fresh = sum(1 for r in results if r.new_alert)
    resolved = sum(1 for r in results if r.resolved)
    parts = [f"{sensor_count} capteur(s) verifie(s)"]
    if fresh:
        parts.append(f"{fresh} nouvelle(s) alerte(s)")
    if active:
        parts.append(f"{active} hors seuil (deja active)")
    if resolved:
        parts.append(f"{resolved} retour conforme")
    if not fresh and not active and not resolved:
        parts.append("tous conformes")
    print(f"[{stamp} UTC] {' | '.join(parts)}")


def _send_discord_alert(ctx: PaysSeuils, lot_id: str, temperature: float, humidity: float) -> bool:
    url = os.getenv("DISCORD_WEBHOOK_URL", "")
    if not url:
        logger.debug("DISCORD_WEBHOOK_URL absent - alerte Discord ignoree")
        return False
    embed = build_condition_embed(
        pays_slug=ctx.slug,
        pays_label=PAYS_LABEL.get(ctx.code, ctx.code),
        entrepot=ctx.entrepot_nom,
        lot_id=lot_id,
        temperature=temperature,
        humidity=humidity,
        temp_min=ctx.temp_min,
        temp_max=ctx.temp_max,
        hum_min=ctx.hum_min,
        hum_max=ctx.hum_max,
    )
    payload = webhook_payload(embed)
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "User-Agent": "FutureKawa-Monitor/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10):
            logger.info("Alerte Discord envoyee (%s)", ctx.slug)
            return True
    except urllib.error.URLError as exc:
        logger.warning("Echec Discord : %s", exc)
        return False


def process_releve(
    cnx,
    capteur_id: str,
    temperature: float,
    humidity: float,
) -> ReleveCheckResult | None:
    """Verifie les seuils apres INSERT releve_capteur."""
    cur = cnx.cursor(dictionary=True)
    try:
        ctx = _load_context(cur, capteur_id)
        if not ctx:
            return None

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
            return None

        lot_id = str(lot["id"])
        statut = str(lot["statut"] or "CONFORME").upper()

        if alerts:
            if statut != "CONFORME":
                return _build_result(
                    ctx,
                    lot_id,
                    temperature,
                    humidity,
                    tuple(alerts),
                    new_alert=False,
                    resolved=False,
                    discord_sent=False,
                    lot_statut=statut,
                )
            message = f"Lot {lot_id[:8]}... - {ctx.entrepot_nom}\n" + "\n".join(alerts)
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
            discord_sent = _send_discord_alert(ctx, lot_id, temperature, humidity)
            send_condition_email(
                pays_slug=ctx.slug,
                pays_label=PAYS_LABEL.get(ctx.code, ctx.code),
                entrepot=ctx.entrepot_nom,
                lot_id=lot_id,
                temperature=temperature,
                humidity=humidity,
                temp_min=ctx.temp_min,
                temp_max=ctx.temp_max,
                hum_min=ctx.hum_min,
                hum_max=ctx.hum_max,
            )
            return _build_result(
                ctx,
                lot_id,
                temperature,
                humidity,
                tuple(alerts),
                new_alert=True,
                resolved=False,
                discord_sent=discord_sent,
                lot_statut="ALERTE",
            )

        if statut == "ALERTE":
            cur.execute(
                "UPDATE lot SET statut = 'CONFORME' WHERE id = %s",
                (lot_id,),
            )
            cnx.commit()
            return _build_result(
                ctx,
                lot_id,
                temperature,
                humidity,
                (),
                new_alert=False,
                resolved=True,
                discord_sent=False,
                lot_statut="CONFORME",
            )
        return None
    except Exception:
        cnx.rollback()
        logger.exception("Erreur evaluation seuils capteur %s", capteur_id)
        return None
    finally:
        cur.close()
