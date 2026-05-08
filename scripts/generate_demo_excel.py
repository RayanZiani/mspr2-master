import math
import random
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd


UTC = timezone.utc


@dataclass(frozen=True)
class PaysRule:
    code: str
    nom: str
    temperature_ideale_c: float
    humidite_ideale_pct: float
    tolerance_temperature_c: float = 3.0
    tolerance_humidite_pct: float = 2.0
    email_responsable: str = ""


def _dt(s: str) -> datetime:
    # format "YYYY-MM-DD HH:MM"
    return datetime.strptime(s, "%Y-%m-%d %H:%M").replace(tzinfo=UTC)


def _round2(x: float) -> float:
    return float(f"{x:.2f}")


def _make_uuid() -> str:
    return str(uuid.uuid4())


def _seasonal_wave(t: pd.DatetimeIndex, period_days: float, phase: float = 0.0) -> np.ndarray:
    # sinusoidale entre -1 et 1
    seconds = (t.view("int64") // 10**9).astype(np.float64)
    period = period_days * 24 * 3600
    return np.sin(2 * math.pi * (seconds / period + phase))


def main() -> int:
    random.seed(42)
    np.random.seed(42)

    repo_root = Path(__file__).resolve().parents[1]
    out_path = repo_root / "database" / "demo_data.xlsx"

    # Plage demandée: du 08/05 au 31/07 (2026)
    start = _dt("2026-05-08 00:00")
    end = _dt("2026-07-31 23:55")
    index = pd.date_range(start=start, end=end, freq="5min", tz="UTC")

    pays_rules = [
        PaysRule(
            code="BR",
            nom="Brésil",
            temperature_ideale_c=29.0,
            humidite_ideale_pct=55.0,
            email_responsable="responsable.br@futurekawa.local",
        ),
        PaysRule(
            code="EC",
            nom="Équateur",
            temperature_ideale_c=31.0,
            humidite_ideale_pct=60.0,
            email_responsable="responsable.ec@futurekawa.local",
        ),
        PaysRule(
            code="CO",
            nom="Colombie",
            temperature_ideale_c=26.0,
            humidite_ideale_pct=80.0,
            email_responsable="responsable.co@futurekawa.local",
        ),
    ]

    # ---- Tables "référentiel" (IDs explicites pour l’Excel) ----
    pays_rows = []
    exploitation_rows = []
    entrepot_rows = []
    capteur_rows = []
    lot_rows = []

    pays_id_by_code: dict[str, int] = {}
    exploitation_id = 1
    entrepot_id = 1

    for i, p in enumerate(pays_rules, start=1):
        pays_id_by_code[p.code] = i
        pays_rows.append(
            {
                "id": i,
                "code": p.code,
                "nom": p.nom,
                "temperature_ideale_c": p.temperature_ideale_c,
                "humidite_ideale_pct": p.humidite_ideale_pct,
                "tolerance_temperature_c": p.tolerance_temperature_c,
                "tolerance_humidite_pct": p.tolerance_humidite_pct,
                "email_responsable": p.email_responsable,
            }
        )

        # 2 exploitations / pays
        for e_idx in range(1, 3):
            exploitation_rows.append(
                {
                    "id": exploitation_id,
                    "pays_id": i,
                    "nom": f"Exploitation {p.code}-{e_idx}",
                    "cree_le": start.isoformat(),
                }
            )
            # 1 entrepôt / exploitation
            entrepot_rows.append(
                {
                    "id": entrepot_id,
                    "pays_id": i,
                    "exploitation_id": exploitation_id,
                    "nom": f"Entrepôt {p.code}-{e_idx}",
                    "adresse": f"{p.nom} - site {e_idx}",
                    "cree_le": start.isoformat(),
                }
            )

            # 1 capteur / entrepôt
            capteur_id = _make_uuid()
            capteur_rows.append(
                {
                    "id": capteur_id,
                    "entrepot_id": entrepot_id,
                    "numero_serie": f"{p.code}-SENSOR-{e_idx:02d}",
                    "modele": "DHT22",
                    "installe_le": start.isoformat(),
                    "active": 1,
                }
            )

            # 3 lots / entrepôt (échelonnés sur mai/juin/juillet)
            for l_idx in range(1, 4):
                entered = start + timedelta(days=7 * (l_idx - 1) + 3 * (e_idx - 1))
                lot_rows.append(
                    {
                        "id": _make_uuid(),
                        "pays_id": i,
                        "exploitation_id": exploitation_id,
                        "entrepot_id": entrepot_id,
                        "entre_le": entered.isoformat(),
                        "sorti_le": None,
                        "statut": "CONFORME",
                        "cree_le": entered.isoformat(),
                    }
                )

            exploitation_id += 1
            entrepot_id += 1

    df_pays = pd.DataFrame(pays_rows)
    df_exploitation = pd.DataFrame(exploitation_rows)
    df_entrepot = pd.DataFrame(entrepot_rows)
    df_capteur = pd.DataFrame(capteur_rows)
    df_lot = pd.DataFrame(lot_rows)

    # ---- Relevés toutes les 5 minutes ----
    # Pour garder un fichier “démonstration” raisonnable, on génère 1 série / capteur (donc 6 entrepôts -> 6 capteurs)
    capteurs = df_capteur[["id", "entrepot_id"]].to_dict(orient="records")

    # Forme de variation:
    # - bruit léger
    # - cycle quotidien (temp + hum opposés)
    # - une vague lente sur ~20 jours
    daily = _seasonal_wave(index, period_days=1.0, phase=0.0)
    slow = _seasonal_wave(index, period_days=20.0, phase=0.25)
    index_utc_naive = index.tz_convert("UTC").tz_localize(None)

    releves_parts = []
    for cap in capteurs:
        entrepot_id_local = int(cap["entrepot_id"])
        pays_id = int(df_entrepot.loc[df_entrepot["id"] == entrepot_id_local, "pays_id"].iloc[0])
        p = next(x for x in pays_rules if pays_id_by_code[x.code] == pays_id)

        temp = (
            p.temperature_ideale_c
            + 1.2 * daily
            + 0.8 * slow
            + np.random.normal(0.0, 0.35, size=len(index))
        )
        hum = (
            p.humidite_ideale_pct
            - 1.5 * daily
            + 1.0 * slow
            + np.random.normal(0.0, 0.6, size=len(index))
        )

        # Injecte quelques incidents (dépassements) pour “montrer” les alertes
        # 3 fenêtres de 6h où c’est hors tolérance
        for k in range(3):
            incident_start = start + timedelta(days=10 + 20 * k + (entrepot_id_local % 3), hours=8)
            incident_end = incident_start + timedelta(hours=6)
            mask = (index >= incident_start) & (index <= incident_end)
            temp[mask] += (p.tolerance_temperature_c + 1.0)
            hum[mask] -= (p.tolerance_humidite_pct + 1.5)

        hum = np.clip(hum, 0.0, 100.0)

        part = pd.DataFrame(
            {
                "capteur_id": cap["id"],
                "mesure_le": index_utc_naive.astype(str) + "Z",
                "temperature_c": np.round(temp, 2),
                "humidite_pct": np.round(hum, 2),
                "cree_le": (index_utc_naive + pd.Timedelta(seconds=2)).astype(str) + "Z",
            }
        )
        releves_parts.append(part)

    df_releve = pd.concat(releves_parts, ignore_index=True)
    df_releve.insert(0, "id", np.arange(1, len(df_releve) + 1))

    # ---- Alertes (dérivées des relevés + règle > 365j simulée sur 1 lot) ----
    # Alertes "CONDITION": on crée une alerte par fenêtre d’incident (par entrepôt)
    alert_rows = []
    alert_id = 1
    for cap in capteurs:
        entrepot_id_local = int(cap["entrepot_id"])
        pays_id = int(df_entrepot.loc[df_entrepot["id"] == entrepot_id_local, "pays_id"].iloc[0])
        p = next(x for x in pays_rules if pays_id_by_code[x.code] == pays_id)
        for k in range(3):
            opened = start + timedelta(days=10 + 20 * k + (entrepot_id_local % 3), hours=8)
            msg = (
                f"Conditions hors tolérance ({p.code}) sur entrepôt {entrepot_id_local} "
                f"(temp/hum) — action requise."
            )
            alert_rows.append(
                {
                    "id": alert_id,
                    "type": "CONDITION",
                    "pays_id": pays_id,
                    "entrepot_id": entrepot_id_local,
                    "lot_id": None,
                    "ouverte_le": opened.isoformat().replace("+00:00", "Z"),
                    "fermee_le": (opened + timedelta(hours=2)).isoformat().replace("+00:00", "Z"),
                    "email_envoye_le": (opened + timedelta(minutes=1)).isoformat().replace("+00:00", "Z"),
                    "message": msg,
                }
            )
            alert_id += 1

    # Alerte "AGE": on force un lot ancien pour la démo
    old_lot = df_lot.iloc[0].copy()
    old_lot["entre_le"] = (start - timedelta(days=400)).isoformat()
    old_lot["statut"] = "ALERTE"
    df_lot.iloc[0] = old_lot
    alert_rows.append(
        {
            "id": alert_id,
            "type": "AGE",
            "pays_id": int(old_lot["pays_id"]),
            "entrepot_id": int(old_lot["entrepot_id"]),
            "lot_id": old_lot["id"],
            "ouverte_le": start.isoformat().replace("+00:00", "Z"),
            "fermee_le": None,
            "email_envoye_le": (start + timedelta(minutes=2)).isoformat().replace("+00:00", "Z"),
            "message": "Lot stocké depuis plus de 365 jours — rotation FIFO prioritaire.",
        }
    )

    df_alerte = pd.DataFrame(alert_rows)

    # ---- Export Excel ----
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        df_pays.to_excel(writer, sheet_name="pays", index=False)
        df_exploitation.to_excel(writer, sheet_name="exploitation", index=False)
        df_entrepot.to_excel(writer, sheet_name="entrepot", index=False)
        df_lot.to_excel(writer, sheet_name="lot", index=False)
        df_capteur.to_excel(writer, sheet_name="capteur", index=False)
        df_releve.to_excel(writer, sheet_name="releve_capteur", index=False)
        df_alerte.to_excel(writer, sheet_name="alerte", index=False)

    print(f"OK: fichier généré: {out_path}")
    print(f"Relevés générés: {len(df_releve):,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

