from datetime import datetime, timedelta
from api.config import (
    SEUIL_TEMP, SEUIL_HUMIDITY,
    TOLERANCE_TEMP, TOLERANCE_HUMIDITY,
    PEREMPTION_JOURS,
)


def check_alerts(payload: dict) -> list[str]:
    alerts = []

    temp = payload.get("temp")
    humidity = payload.get("humidity")

    if temp is not None and abs(temp - SEUIL_TEMP) > TOLERANCE_TEMP:
        alerts.append(f"ALERTE température : {temp}°C (seuil {SEUIL_TEMP}°C ±{TOLERANCE_TEMP})")

    if humidity is not None and abs(humidity - SEUIL_HUMIDITY) > TOLERANCE_HUMIDITY:
        alerts.append(f"ALERTE humidité : {humidity}% (seuil {SEUIL_HUMIDITY}% ±{TOLERANCE_HUMIDITY})")

    return alerts


def is_lot_perime(date_stockage: datetime) -> bool:
    return (datetime.utcnow() - date_stockage).days > PEREMPTION_JOURS
