"""Seuils IoT par pays (table `pays` sur Aiven)."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from api.config import PAYS_SLUG

PAYS_SQL = text("""
    SELECT
        id,
        code,
        nom,
        temperature_ideale_c,
        humidite_ideale_pct,
        tolerance_temperature_c,
        tolerance_humidite_pct
    FROM pays
    ORDER BY code
""")


@dataclass(frozen=True)
class Range:
    min: float
    max: float
    ideal: float


@dataclass(frozen=True)
class PaysSeuils:
    code: str
    nom: str
    slug: str
    pays_id: int
    temperature: Range
    humidity: Range


def _range_from_row(is_temperature: bool, row: dict) -> Range:
    if is_temperature:
        ideal = float(row["temperature_ideale_c"])
        tol = float(row["tolerance_temperature_c"])
    else:
        ideal = float(row["humidite_ideale_pct"])
        tol = float(row["tolerance_humidite_pct"])
    return Range(min=round(ideal - tol, 2), max=round(ideal + tol, 2), ideal=round(ideal, 2))


def row_to_seuils(row: dict) -> PaysSeuils:
    code = str(row["code"]).upper()
    return PaysSeuils(
        code=code,
        nom=str(row["nom"]),
        slug=PAYS_SLUG.get(code, code.lower()),
        pays_id=int(row["id"]),
        temperature=_range_from_row(True, row),
        humidity=_range_from_row(False, row),
    )


def seuils_to_dict(seuils: PaysSeuils) -> dict:
    return {
        "code": seuils.code,
        "nom": seuils.nom,
        "slug": seuils.slug,
        "temperature": {
            "min": seuils.temperature.min,
            "max": seuils.temperature.max,
            "ideal": seuils.temperature.ideal,
        },
        "humidity": {
            "min": seuils.humidity.min,
            "max": seuils.humidity.max,
            "ideal": seuils.humidity.ideal,
        },
    }


def ranges_to_db_values(
    temp_min: float,
    temp_max: float,
    hum_min: float,
    hum_max: float,
) -> dict[str, float]:
    if temp_min >= temp_max:
        raise ValueError("temperature_min doit etre inferieur a temperature_max")
    if hum_min >= hum_max:
        raise ValueError("humidity_min doit etre inferieur a humidity_max")
    return {
        "temperature_ideale_c": round((temp_min + temp_max) / 2, 2),
        "tolerance_temperature_c": round((temp_max - temp_min) / 2, 2),
        "humidite_ideale_pct": round((hum_min + hum_max) / 2, 2),
        "tolerance_humidite_pct": round((hum_max - hum_min) / 2, 2),
    }


async def list_pays_seuils(session: AsyncSession) -> list[PaysSeuils]:
    result = await session.execute(PAYS_SQL)
    return [row_to_seuils(dict(row)) for row in result.mappings().all()]


async def get_pays_seuils(session: AsyncSession, code: str) -> PaysSeuils | None:
    sql = text("""
        SELECT
            id, code, nom,
            temperature_ideale_c, humidite_ideale_pct,
            tolerance_temperature_c, tolerance_humidite_pct
        FROM pays
        WHERE code = :code
        LIMIT 1
    """)
    result = await session.execute(sql, {"code": code.upper()})
    row = result.mappings().first()
    return row_to_seuils(dict(row)) if row else None


async def update_pays_seuils(
    session: AsyncSession,
    code: str,
    temp_min: float,
    temp_max: float,
    hum_min: float,
    hum_max: float,
) -> PaysSeuils | None:
    values = ranges_to_db_values(temp_min, temp_max, hum_min, hum_max)
    sql = text("""
        UPDATE pays SET
            temperature_ideale_c = :temperature_ideale_c,
            tolerance_temperature_c = :tolerance_temperature_c,
            humidite_ideale_pct = :humidite_ideale_pct,
            tolerance_humidite_pct = :tolerance_humidite_pct
        WHERE code = :code
    """)
    await session.execute(sql, {**values, "code": code.upper()})
    await session.commit()
    return await get_pays_seuils(session, code)
