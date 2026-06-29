"""CRUD lots, entrepôts et exploitations sur Aiven MySQL."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from api.config import PAYS_SLUG, STATUT_FRONT
from api.db.database import SessionLocal
from api.services.redis_cache import delete_cache_prefix

SLUG_TO_CODE = {slug: code for code, slug in PAYS_SLUG.items()}

STATUT_DB = {
    "conforme": "CONFORME",
    "alerte": "ALERTE",
    "perime": "PERIME",
    "expedie": "EXPEDIE",
}


def _dt_iso(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def _pays_filter_sql(allowed_slugs: set[str] | None, alias: str = "p") -> tuple[str, dict]:
    if allowed_slugs is None:
        return "", {}
    codes = [SLUG_TO_CODE[s] for s in allowed_slugs if s in SLUG_TO_CODE]
    if not codes:
        return " AND 1=0", {}
    placeholders = ", ".join(f":pc{i}" for i in range(len(codes)))
    params = {f"pc{i}": code for i, code in enumerate(codes)}
    return f" AND {alias}.code IN ({placeholders})", params


async def _resolve_pays_id(session: AsyncSession, pays_slug: str) -> int:
    code = SLUG_TO_CODE.get(pays_slug)
    if not code:
        raise ValueError("Pays inconnu")
    res = await session.execute(
        text("SELECT id FROM pays WHERE code = :code LIMIT 1"),
        {"code": code},
    )
    row = res.mappings().first()
    if not row:
        raise ValueError("Pays inconnu")
    return int(row["id"])


async def list_exploitations(allowed_slugs: set[str] | None) -> list[dict]:
    filt, params = _pays_filter_sql(allowed_slugs)
    sql = text(f"""
        SELECT e.id, p.code AS pays_code, e.nom, e.cree_le
        FROM exploitation e
        INNER JOIN pays p ON p.id = e.pays_id
        WHERE 1=1{filt}
        ORDER BY p.code, e.nom
    """)
    async with SessionLocal() as session:
        res = await session.execute(sql, params)
        return [
            {
                "id": int(r["id"]),
                "pays": PAYS_SLUG.get(r["pays_code"], str(r["pays_code"]).lower()),
                "pays_code": r["pays_code"],
                "nom": r["nom"],
                "cree_le": _dt_iso(r["cree_le"]),
            }
            for r in res.mappings().all()
        ]


async def create_exploitation(pays_slug: str, nom: str) -> dict:
    nom = (nom or "").strip()
    if not nom:
        raise ValueError("Nom d'exploitation requis")
    async with SessionLocal() as session:
        pays_id = await _resolve_pays_id(session, pays_slug)
        await session.execute(
            text("INSERT INTO exploitation (pays_id, nom) VALUES (:pays_id, :nom)"),
            {"pays_id": pays_id, "nom": nom},
        )
        await session.commit()
        res = await session.execute(
            text("""
                SELECT e.id, p.code AS pays_code, e.nom, e.cree_le
                FROM exploitation e
                INNER JOIN pays p ON p.id = e.pays_id
                WHERE e.pays_id = :pays_id AND e.nom = :nom
                ORDER BY e.id DESC LIMIT 1
            """),
            {"pays_id": pays_id, "nom": nom},
        )
        row = dict(res.mappings().first())
    await delete_cache_prefix("siege:stocks")
    return {
        "id": int(row["id"]),
        "pays": PAYS_SLUG.get(row["pays_code"], pays_slug),
        "nom": row["nom"],
        "cree_le": _dt_iso(row["cree_le"]),
    }


async def update_exploitation(exploitation_id: int, nom: str) -> None:
    nom = (nom or "").strip()
    if not nom:
        raise ValueError("Nom d'exploitation requis")
    async with SessionLocal() as session:
        res = await session.execute(
            text("UPDATE exploitation SET nom = :nom WHERE id = :id"),
            {"id": exploitation_id, "nom": nom},
        )
        await session.commit()
        if res.rowcount == 0:
            raise ValueError("Exploitation introuvable")
    await delete_cache_prefix("siege:stocks")


async def delete_exploitation(exploitation_id: int) -> None:
    async with SessionLocal() as session:
        try:
            res = await session.execute(
                text("DELETE FROM exploitation WHERE id = :id"),
                {"id": exploitation_id},
            )
            await session.commit()
        except Exception as exc:
            await session.rollback()
            raise ValueError("Impossible de supprimer : exploitation utilisée") from exc
        if res.rowcount == 0:
            raise ValueError("Exploitation introuvable")
    await delete_cache_prefix("siege:stocks")


async def list_entrepots(allowed_slugs: set[str] | None) -> list[dict]:
    filt, params = _pays_filter_sql(allowed_slugs)
    sql = text(f"""
        SELECT e.id, p.code AS pays_code, e.nom, e.adresse, e.exploitation_id,
               exp.nom AS exploitation_nom, e.cree_le
        FROM entrepot e
        INNER JOIN pays p ON p.id = e.pays_id
        LEFT JOIN exploitation exp ON exp.id = e.exploitation_id
        WHERE 1=1{filt}
        ORDER BY p.code, e.nom
    """)
    async with SessionLocal() as session:
        res = await session.execute(sql, params)
        return [
            {
                "id": int(r["id"]),
                "pays": PAYS_SLUG.get(r["pays_code"], str(r["pays_code"]).lower()),
                "nom": r["nom"],
                "adresse": r["adresse"],
                "exploitation_id": r["exploitation_id"],
                "exploitation_nom": r["exploitation_nom"],
                "cree_le": _dt_iso(r["cree_le"]),
            }
            for r in res.mappings().all()
        ]


async def create_entrepot(
    pays_slug: str,
    nom: str,
    exploitation_id: int | None,
    adresse: str | None,
) -> dict:
    nom = (nom or "").strip()
    if not nom:
        raise ValueError("Nom d'entrepôt requis")
    async with SessionLocal() as session:
        pays_id = await _resolve_pays_id(session, pays_slug)
        await session.execute(
            text("""
                INSERT INTO entrepot (pays_id, exploitation_id, nom, adresse)
                VALUES (:pays_id, :exploitation_id, :nom, :adresse)
            """),
            {
                "pays_id": pays_id,
                "exploitation_id": exploitation_id,
                "nom": nom,
                "adresse": (adresse or "").strip() or None,
            },
        )
        await session.commit()
        res = await session.execute(
            text("""
                SELECT e.id, p.code AS pays_code, e.nom, e.adresse, e.exploitation_id,
                       exp.nom AS exploitation_nom, e.cree_le
                FROM entrepot e
                INNER JOIN pays p ON p.id = e.pays_id
                LEFT JOIN exploitation exp ON exp.id = e.exploitation_id
                WHERE e.pays_id = :pays_id AND e.nom = :nom
                ORDER BY e.id DESC LIMIT 1
            """),
            {"pays_id": pays_id, "nom": nom},
        )
        row = dict(res.mappings().first())
    await delete_cache_prefix("siege:stocks")
    return {
        "id": int(row["id"]),
        "pays": PAYS_SLUG.get(row["pays_code"], pays_slug),
        "nom": row["nom"],
        "adresse": row["adresse"],
        "exploitation_id": row["exploitation_id"],
        "exploitation_nom": row["exploitation_nom"],
        "cree_le": _dt_iso(row["cree_le"]),
    }


async def update_entrepot(
    entrepot_id: int,
    nom: str | None,
    adresse: str | None,
    exploitation_id: int | None,
) -> None:
    async with SessionLocal() as session:
        fields = []
        params: dict[str, Any] = {"id": entrepot_id}
        if nom is not None:
            n = nom.strip()
            if not n:
                raise ValueError("Nom d'entrepôt requis")
            fields.append("nom = :nom")
            params["nom"] = n
        if adresse is not None:
            fields.append("adresse = :adresse")
            params["adresse"] = adresse.strip() or None
        if exploitation_id is not None:
            fields.append("exploitation_id = :exploitation_id")
            params["exploitation_id"] = exploitation_id
        if not fields:
            return
        res = await session.execute(
            text(f"UPDATE entrepot SET {', '.join(fields)} WHERE id = :id"),
            params,
        )
        await session.commit()
        if res.rowcount == 0:
            raise ValueError("Entrepôt introuvable")
    await delete_cache_prefix("siege:stocks")


async def delete_entrepot(entrepot_id: int) -> None:
    async with SessionLocal() as session:
        try:
            res = await session.execute(
                text("DELETE FROM entrepot WHERE id = :id"),
                {"id": entrepot_id},
            )
            await session.commit()
        except Exception as exc:
            await session.rollback()
            raise ValueError("Impossible de supprimer : entrepôt utilisé") from exc
        if res.rowcount == 0:
            raise ValueError("Entrepôt introuvable")
    await delete_cache_prefix("siege:stocks")


async def list_lots_manage(allowed_slugs: set[str] | None) -> list[dict]:
    filt, params = _pays_filter_sql(allowed_slugs, alias="p")
    sql = text(f"""
        SELECT l.id, p.code AS pays_code, exp.nom AS exploitation, e.nom AS entrepot,
               l.entre_le, l.sorti_le, l.statut,
               l.exploitation_id, l.entrepot_id
        FROM lot l
        INNER JOIN pays p ON p.id = l.pays_id
        INNER JOIN exploitation exp ON exp.id = l.exploitation_id
        INNER JOIN entrepot e ON e.id = l.entrepot_id
        WHERE l.sorti_le IS NULL{filt}
        ORDER BY p.code, l.entre_le ASC
    """)
    async with SessionLocal() as session:
        res = await session.execute(sql, params)
        return [_map_lot_row(dict(r)) for r in res.mappings().all()]


def _map_lot_row(row: dict) -> dict:
    statut_db = (row.get("statut") or "CONFORME").upper()
    return {
        "id": str(row["id"]),
        "pays": PAYS_SLUG.get(row["pays_code"], str(row["pays_code"]).lower()),
        "exploitation": row.get("exploitation") or "",
        "entrepot": row.get("entrepot") or "",
        "exploitation_id": int(row["exploitation_id"]),
        "entrepot_id": int(row["entrepot_id"]),
        "date_stockage": _dt_iso(row.get("entre_le")),
        "sorti_le": _dt_iso(row.get("sorti_le")),
        "statut": STATUT_FRONT.get(statut_db, "conforme"),
    }


async def create_lot(
    exploitation_id: int,
    entrepot_id: int,
    entre_le: datetime | None = None,
    allowed_slugs: set[str] | None = None,
) -> dict:
    when = entre_le or datetime.now(timezone.utc).replace(tzinfo=None)
    lot_id = str(uuid.uuid4())
    async with SessionLocal() as session:
        check = await session.execute(
            text("""
                SELECT e.pays_id, ent.pays_id AS ent_pays_id, ent.exploitation_id, p.code AS pays_code
                FROM entrepot ent
                INNER JOIN exploitation e ON e.id = :exploitation_id
                INNER JOIN pays p ON p.id = e.pays_id
                WHERE ent.id = :entrepot_id
                LIMIT 1
            """),
            {"exploitation_id": exploitation_id, "entrepot_id": entrepot_id},
        )
        row = check.mappings().first()
        if not row or row["pays_id"] != row["ent_pays_id"]:
            raise ValueError("Entrepôt et exploitation incompatibles")
        if row["exploitation_id"] and int(row["exploitation_id"]) != exploitation_id:
            raise ValueError("Entrepôt et exploitation incompatibles")
        slug = PAYS_SLUG.get(row["pays_code"])
        if allowed_slugs is not None and slug not in allowed_slugs:
            raise ValueError("Pays non autorisé")
        pays_id = int(row["pays_id"])
        await session.execute(
            text("""
                INSERT INTO lot (id, pays_id, exploitation_id, entrepot_id, entre_le, statut)
                VALUES (:id, :pays_id, :exploitation_id, :entrepot_id, :entre_le, 'CONFORME')
            """),
            {
                "id": lot_id,
                "pays_id": pays_id,
                "exploitation_id": exploitation_id,
                "entrepot_id": entrepot_id,
                "entre_le": when,
            },
        )
        await session.commit()
    await delete_cache_prefix("siege:stocks")
    lots = await list_lots_manage(None)
    return next((lot for lot in lots if lot["id"] == lot_id), {"id": lot_id})


async def update_lot(lot_id: str, statut: str | None, expedier: bool) -> None:
    async with SessionLocal() as session:
        if expedier:
            await session.execute(
                text("""
                    UPDATE lot SET statut = 'EXPEDIE', sorti_le = UTC_TIMESTAMP(3)
                    WHERE id = :id AND sorti_le IS NULL
                """),
                {"id": lot_id},
            )
        elif statut:
            db_statut = STATUT_DB.get(statut.lower())
            if not db_statut:
                raise ValueError("Statut invalide")
            await session.execute(
                text("UPDATE lot SET statut = :statut WHERE id = :id"),
                {"id": lot_id, "statut": db_statut},
            )
        else:
            return
        await session.commit()
    await delete_cache_prefix("siege:stocks")


async def get_lot_pays_slug_by_id(lot_id: str) -> str | None:
    sql = text("""
        SELECT p.code AS pays_code FROM lot l
        INNER JOIN pays p ON p.id = l.pays_id
        WHERE l.id = :lot_id LIMIT 1
    """)
    async with SessionLocal() as session:
        res = await session.execute(sql, {"lot_id": lot_id})
        row = res.mappings().first()
        if not row:
            return None
        return PAYS_SLUG.get(row["pays_code"])
