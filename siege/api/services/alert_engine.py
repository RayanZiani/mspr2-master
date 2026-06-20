"""Evaluation des releves vs seuils + mise a jour lots / alertes / Discord."""

from __future__ import annotations

import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from api.services.threshold_service import PaysSeuils, row_to_seuils
from api.services.webhook_service import send_condition_alert

logger = logging.getLogger(__name__)


def check_reading(seuils: PaysSeuils, temperature: float, humidity: float) -> list[str]:
    messages: list[str] = []
    t = seuils.temperature
    h = seuils.humidity
    if temperature < t.min or temperature > t.max:
        messages.append(
            f"Temperature {temperature:.1f} C hors plage [{t.min:.1f} ; {t.max:.1f}] C"
        )
    if humidity < h.min or humidity > h.max:
        messages.append(
            f"Humidite {humidity:.1f} % hors plage [{h.min:.1f} ; {h.max:.1f}] %"
        )
    return messages


async def process_releve_for_capteur(
    session: AsyncSession,
    capteur_id: str,
    temperature: float,
    humidity: float,
) -> None:
    ctx_sql = text("""
        SELECT
            p.id AS pays_id,
            p.code AS pays_code,
            p.nom AS pays_nom,
            p.temperature_ideale_c,
            p.humidite_ideale_pct,
            p.tolerance_temperature_c,
            p.tolerance_humidite_pct,
            e.id AS entrepot_id,
            e.nom AS entrepot_nom
        FROM capteur c
        INNER JOIN entrepot e ON e.id = c.entrepot_id
        INNER JOIN pays p ON p.id = e.pays_id
        WHERE c.id = :capteur_id
        LIMIT 1
    """)
    ctx_res = await session.execute(ctx_sql, {"capteur_id": capteur_id})
    ctx = ctx_res.mappings().first()
    if not ctx:
        return

    seuils = row_to_seuils(dict(ctx))
    alerts = check_reading(seuils, temperature, humidity)

    lot_sql = text("""
        SELECT l.id, l.statut
        FROM lot l
        WHERE l.entrepot_id = :entrepot_id AND l.sorti_le IS NULL
        ORDER BY l.entre_le ASC
        LIMIT 1
    """)
    lot_res = await session.execute(lot_sql, {"entrepot_id": ctx["entrepot_id"]})
    lot = lot_res.mappings().first()
    if not lot:
        return

    lot_id = str(lot["id"])
    statut = str(lot["statut"] or "CONFORME").upper()

    if alerts:
        if statut == "CONFORME":
            await session.execute(
                text("UPDATE lot SET statut = 'ALERTE' WHERE id = :lot_id"),
                {"lot_id": lot_id},
            )
            message = (
                f"Lot {lot_id[:8]}… — {ctx['entrepot_nom']}\n"
                + "\n".join(alerts)
            )
            await session.execute(
                text("""
                    INSERT INTO alerte (type, pays_id, entrepot_id, lot_id, message)
                    VALUES ('CONDITION', :pays_id, :entrepot_id, :lot_id, :message)
                """),
                {
                    "pays_id": ctx["pays_id"],
                    "entrepot_id": ctx["entrepot_id"],
                    "lot_id": lot_id,
                    "message": message,
                },
            )
            await session.commit()
            await send_condition_alert(
                pays_slug=seuils.slug,
                pays_label=seuils.nom,
                entrepot=str(ctx["entrepot_nom"]),
                lot_id=lot_id,
                temperature=temperature,
                humidity=humidity,
                temp_min=seuils.temperature.min,
                temp_max=seuils.temperature.max,
                hum_min=seuils.humidity.min,
                hum_max=seuils.humidity.max,
            )
    elif statut == "ALERTE":
        await session.execute(
            text("UPDATE lot SET statut = 'CONFORME' WHERE id = :lot_id"),
            {"lot_id": lot_id},
        )
        await session.commit()
