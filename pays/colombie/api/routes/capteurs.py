"""Route REST pour l'état de connexion des capteurs IoT — Brésil."""

from fastapi import APIRouter

from api.services.mqtt_subscriber import get_capteur_status, CAPTEUR_TIMEOUT_SECONDS

router = APIRouter()


@router.get("/status")
async def capteurs_status():
    """
    Retourne le statut de connexion de chaque entrepôt.

    Un capteur est considéré 'disconnected' si aucune mesure n'a été reçue
    depuis plus de CAPTEUR_TIMEOUT secondes (défaut : 300s / 5 min).
    """
    status = get_capteur_status()
    return {
        "timeout_seconds": CAPTEUR_TIMEOUT_SECONDS,
        "capteurs": status,
        "summary": {
            "total": len(status),
            "connected": sum(1 for v in status.values() if v["connected"]),
            "disconnected": sum(1 for v in status.values() if not v["connected"]),
        },
    }
