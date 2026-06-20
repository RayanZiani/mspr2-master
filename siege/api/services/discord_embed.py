"""Construction d'embeds Discord riches (Markdown — pas de HTML supporte par Discord)."""

from __future__ import annotations

from datetime import datetime, timezone

_COLORS = {
    "condition": 0xE74C3C,
    "peremption": 0xE67E22,
    "connection": 0xF1C40F,
    "test": 0x3498DB,
    "ok": 0x2ECC71,
}


def _status_line(ok: bool, label: str, value: float, unit: str, lo: float, hi: float) -> str:
    badge = "CONFORME" if ok else "**HORS SEUIL**"
    icon = ":white_check_mark:" if ok else ":red_circle:"
    return (
        f"{icon} **{label}** : `{value:.1f}{unit}`\n"
        f"> Plage autorisee : `{lo:.1f}` — `{hi:.1f}{unit}`\n"
        f"> Statut : {badge}"
    )


def build_condition_embed(
    *,
    pays_slug: str,
    pays_label: str,
    entrepot: str,
    lot_id: str,
    temperature: float,
    humidity: float,
    temp_min: float,
    temp_max: float,
    hum_min: float,
    hum_max: float,
) -> dict:
    """Embed structure pour alerte temperature / humidite."""
    temp_ok = temp_min <= temperature <= temp_max
    hum_ok = hum_min <= humidity <= hum_max
    now = datetime.now(timezone.utc).isoformat()

    return {
        "title": f":thermometer: ALERTE FutureKawa — {pays_label.upper()}",
        "url": "https://mspr2-master-front.onrender.com/alertes",
        "description": (
            f"Releve capteur **hors plage** sur **{entrepot}**.\n"
            f"Consultez le [tableau de bord](https://mspr2-master-front.onrender.com/alertes)."
        ),
        "color": _COLORS["condition"],
        "fields": [
            {"name": ":world_map: Pays", "value": f"**{pays_label}** (`{pays_slug.upper()}`)", "inline": True},
            {"name": ":office: Entrepot", "value": f"**{entrepot}**", "inline": True},
            {"name": ":package: Lot", "value": f"`{lot_id[:8]}...`", "inline": True},
            {
                "name": ":thermometer: Temperature",
                "value": _status_line(temp_ok, "Mesure", temperature, " C", temp_min, temp_max),
                "inline": False,
            },
            {
                "name": ":droplet: Humidite",
                "value": _status_line(hum_ok, "Mesure", humidity, " %", hum_min, hum_max),
                "inline": False,
            },
        ],
        "footer": {"text": "FutureKawa IoT Monitoring • Seuils configurables sur /config/capteurs"},
        "timestamp": now,
    }


def build_test_webhook_embed(*, triggered_by: str, environment: str) -> dict:
    """Embed de validation manuelle du webhook Discord (super admin)."""
    now = datetime.now(timezone.utc)
    return {
        "title": ":white_check_mark: Validation webhook Discord — FutureKawa",
        "url": "https://mspr2-master-front.onrender.com/config/capteurs",
        "description": (
            "Test manuel declenche depuis **Configuration capteurs**.\n"
            "Si vous recevez ce message, le canal de notification siege est **operationnel**."
        ),
        "color": _COLORS["ok"],
        "fields": [
            {
                "name": ":bust_in_silhouette: Declenche par",
                "value": f"**{triggered_by}**",
                "inline": True,
            },
            {
                "name": ":globe_with_meridians: Environnement",
                "value": f"`{environment}`",
                "inline": True,
            },
            {
                "name": ":clipboard: Verifications effectuees",
                "value": (
                    ":white_check_mark: Connexion API → Discord\n"
                    ":white_check_mark: Format embed Markdown\n"
                    ":white_check_mark: Canal alertes IoT siege\n"
                    ":white_check_mark: Horodatage UTC"
                ),
                "inline": False,
            },
            {
                "name": ":information_source: Prochaines etapes",
                "value": (
                    "• Ajuster les seuils sur "
                    "[/config/capteurs](https://mspr2-master-front.onrender.com/config/capteurs)\n"
                    "• Surveiller les alertes reelles sur "
                    "[/alertes](https://mspr2-master-front.onrender.com/alertes)"
                ),
                "inline": False,
            },
        ],
        "footer": {"text": "FutureKawa IoT Monitoring • Test webhook super admin"},
        "timestamp": now.isoformat(),
    }


def build_message_embed(
    text: str,
    pays: str,
    alert_type: str = "condition",
) -> dict:
    """Embed generique pour texte libre (test, digest, connexion)."""
    titles = {
        "condition": ":warning: Alerte conditions",
        "peremption": ":hourglass: Alerte peremption",
        "connection": ":satellite: Alerte connexion capteur",
        "test": ":white_check_mark: Test webhook",
    }
    title = titles.get(alert_type, ":bell: Notification")
    color = _COLORS.get(alert_type, _COLORS["condition"])

    lines = []
    for raw in text.strip().splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("- "):
            lines.append(f"• {line[2:]}")
        else:
            lines.append(line)

    body = "\n".join(lines) if lines else text
    return {
        "title": f"{title} — {pays.upper()}",
        "description": body,
        "color": color,
        "footer": {"text": "FutureKawa IoT Monitoring"},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def webhook_payload(embed: dict) -> dict:
    return {"embeds": [embed]}
