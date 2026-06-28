"""Règles d'alerte et de péremption pour la Colombie."""

from datetime import datetime, timezone

from api.config import (
    PEREMPTION_JOURS,
    SEUIL_HUMIDITY,
    SEUIL_TEMP,
    TOLERANCE_HUMIDITY,
    TOLERANCE_TEMP,
)


def check_alerts(payload: dict) -> list[str]:
    """Retourne les messages d'alerte pour une mesure IoT."""
    alerts = []

    temp = payload.get("temp")
    humidity = payload.get("humidity")

    if temp is not None and abs(temp - SEUIL_TEMP) > TOLERANCE_TEMP:
        alerts.append(
            f"ALERTE température : {temp}°C (seuil {SEUIL_TEMP}°C ±{TOLERANCE_TEMP})"
        )

    if humidity is not None and abs(humidity - SEUIL_HUMIDITY) > TOLERANCE_HUMIDITY:
        alerts.append(
            f"ALERTE humidité : {humidity}% "
            f"(seuil {SEUIL_HUMIDITY}% ±{TOLERANCE_HUMIDITY})"
        )

    return alerts


def is_lot_perime(date_stockage: datetime) -> bool:
    """Indique si un lot a dépassé la durée de péremption autorisée."""
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    return (now - date_stockage).days > PEREMPTION_JOURS
