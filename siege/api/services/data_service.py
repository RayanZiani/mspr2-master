"""Lecture agrégée des stocks, mesures et alertes depuis MySQL."""

from datetime import datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from api.config import MESURES_DAYS, MESURES_LIMIT, PAYS_SLUG, STATUT_FRONT
from api.db.database import SessionLocal
from api.services.redis_cache import STOCKS_CACHE_PREFIX, get_cache, set_cache

LOTS_SQL = text("""
    SELECT
        l.id,
        p.code AS pays_code,
        exp.nom AS exploitation,
        e.nom AS entrepot,
        l.entre_le AS date_stockage,
        l.statut
    FROM lot l
    INNER JOIN pays p ON p.id = l.pays_id
    INNER JOIN exploitation exp ON exp.id = l.exploitation_id
    INNER JOIN entrepot e ON e.id = l.entrepot_id
    WHERE l.sorti_le IS NULL
    ORDER BY p.code, l.entre_le ASC
""")


def _mesures_sql() -> text:
    days = max(1, min(MESURES_DAYS, 365))
    limit = max(100, min(MESURES_LIMIT, 20000))
    return text(f"""
        SELECT
            r.id,
            l.id AS lot_id,
            r.mesure_le AS timestamp,
            r.temperature_c AS temperature,
            r.humidite_pct AS humidity
        FROM lot l
        INNER JOIN capteur c ON c.entrepot_id = l.entrepot_id
        INNER JOIN releve_capteur r ON r.capteur_id = c.id
        WHERE l.id = :lot_id
          AND r.mesure_le >= (UTC_TIMESTAMP(3) - INTERVAL {days} DAY)
        ORDER BY r.mesure_le DESC
        LIMIT {limit}
    """)


def _dt_iso(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def _map_lot(row: dict) -> dict:
    pays_code = (row.get("pays_code") or "").upper()
    statut_db = (row.get("statut") or "CONFORME").upper()
    return {
        "id": str(row["id"]),
        "pays": PAYS_SLUG.get(pays_code, pays_code.lower()),
        "exploitation": row.get("exploitation") or "",
        "entrepot": row.get("entrepot") or "",
        "date_stockage": _dt_iso(row.get("date_stockage")),
        "statut": STATUT_FRONT.get(statut_db, "conforme"),
    }


def _map_mesure(row: dict) -> dict:
    return {
        "id": int(row["id"]),
        "lot_id": str(row["lot_id"]),
        "timestamp": _dt_iso(row.get("timestamp")),
        "temperature": float(row["temperature"]),
        "humidity": float(row["humidity"]),
    }


def _group_by_pays(lots: list[dict]) -> list[dict]:
    buckets: dict[str, list[dict]] = {}
    for lot in lots:
        buckets.setdefault(lot["pays"], []).append(lot)
    return [{"pays": pays, "data": items} for pays, items in sorted(buckets.items())]


async def _fetch_lots(session: AsyncSession) -> list[dict]:
    result = await session.execute(LOTS_SQL)
    return [_map_lot(dict(row)) for row in result.mappings().all()]


async def get_stocks_grouped() -> list[dict]:
    cache_key = STOCKS_CACHE_PREFIX
    cached = await get_cache(cache_key)
    if cached is not None:
        return cached

    async with SessionLocal() as session:
        lots = await _fetch_lots(session)

    grouped = _group_by_pays(lots)
    await set_cache(cache_key, grouped)
    return grouped


async def get_mesures_for_lot(lot_id: str) -> list[dict]:
    cache_key = f"siege:mesures:{lot_id}"
    cached = await get_cache(cache_key)
    if cached is not None:
        return cached

    async with SessionLocal() as session:
        result = await session.execute(_mesures_sql(), {"lot_id": lot_id})
        mesures = [_map_mesure(dict(row)) for row in result.mappings().all()]

    await set_cache(cache_key, mesures, ttl=30)
    return mesures


async def get_lot_pays_slug(lot_id: str) -> str | None:
    sql = text(
        """
        SELECT p.code AS pays_code
        FROM lot l
        INNER JOIN pays p ON p.id = l.pays_id
        WHERE l.id = :lot_id
        LIMIT 1
        """
    )
    async with SessionLocal() as session:
        res = await session.execute(sql, {"lot_id": lot_id})
        row = res.mappings().first()
        if not row:
            return None
        pays_code = (row.get("pays_code") or "").upper()
        return PAYS_SLUG.get(pays_code, pays_code.lower() if pays_code else None)


async def get_alertes_grouped() -> list[dict]:
    grouped = await get_stocks_grouped()
    return [
        {
            "pays": block["pays"],
            "data": [lot for lot in block["data"] if lot["statut"] != "conforme"],
        }
        for block in grouped
        if any(lot["statut"] != "conforme" for lot in block["data"])
    ]
