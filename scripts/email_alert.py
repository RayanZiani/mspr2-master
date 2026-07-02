"""Alertes e-mail via Gmail SMTP (compte gratuit) — complement de l'alerte Discord.

Gmail gratuit n'expose pas d'API REST d'envoi : on passe par SMTP avec un
**mot de passe d'application** (16 caracteres) genere depuis
https://myaccount.google.com/apppasswords (2FA obligatoire sur le compte).

Configuration (.env racine) :
  GMAIL_ALERT_USER=futurekawa.alertes@gmail.com
  GMAIL_APP_PASSWORD=abcd efgh ijkl mnop        # mot de passe d'application (16 car.)
  ALERT_EMAIL_TO=supervision@futurekawa.com,ops@futurekawa.com
  GMAIL_SMTP_HOST=smtp.gmail.com                # optionnel
  GMAIL_SMTP_PORT=587                           # optionnel (STARTTLS)

Ce module reprend la meme signature que `_send_discord_alert` (threshold_alert.py)
pour pouvoir etre branche a cote — ou a la place — de la notification Discord.

Usage direct (envoi d'un e-mail de test) :
  python scripts/email_alert.py --test
  python scripts/email_alert.py --demo-condition
"""

from __future__ import annotations

import argparse
import logging
import os
import smtplib
import ssl
from dataclasses import dataclass
from datetime import datetime, timezone
from email.message import EmailMessage
from email.utils import formataddr, formatdate, make_msgid
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(REPO_ROOT / ".env")

logger = logging.getLogger(__name__)

DASHBOARD_URL = "https://mspr2-master-front.onrender.com/alertes"


@dataclass(frozen=True)
class GmailConfig:
    """Parametres SMTP Gmail charges depuis l'environnement."""

    user: str
    app_password: str
    recipients: tuple[str, ...]
    host: str = "smtp.gmail.com"
    port: int = 587
    sender_name: str = "FutureKawa IoT"

    @property
    def is_configured(self) -> bool:
        return bool(self.user and self.app_password and self.recipients)

    @classmethod
    def from_env(cls) -> "GmailConfig":
        raw_to = os.getenv("ALERT_EMAIL_TO", "")
        recipients = tuple(
            addr.strip() for addr in raw_to.split(",") if addr.strip()
        )
        return cls(
            user=os.getenv("GMAIL_ALERT_USER", "").strip(),
            app_password=os.getenv("GMAIL_APP_PASSWORD", "").replace(" ", "").strip(),
            recipients=recipients,
            host=os.getenv("GMAIL_SMTP_HOST", "smtp.gmail.com").strip(),
            port=int(os.getenv("GMAIL_SMTP_PORT", "587")),
            sender_name=os.getenv("GMAIL_SENDER_NAME", "FutureKawa IoT").strip(),
        )


def _status_row(label: str, value: float, unit: str, lo: float, hi: float) -> str:
    ok = lo <= value <= hi
    color = "#2ECC71" if ok else "#E74C3C"
    badge = "CONFORME" if ok else "HORS SEUIL"
    return (
        f'<tr>'
        f'<td style="padding:6px 12px;font-weight:600;color:#2c3e50;">{label}</td>'
        f'<td style="padding:6px 12px;font-family:monospace;">{value:.1f}{unit}</td>'
        f'<td style="padding:6px 12px;color:#7f8c8d;">plage {lo:.1f} — {hi:.1f}{unit}</td>'
        f'<td style="padding:6px 12px;font-weight:700;color:{color};">{badge}</td>'
        f'</tr>'
    )


def _build_condition_html(
    *,
    pays_label: str,
    pays_slug: str,
    entrepot: str,
    lot_id: str,
    temperature: float,
    humidity: float,
    temp_min: float,
    temp_max: float,
    hum_min: float,
    hum_max: float,
) -> str:
    stamp = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M:%S UTC")
    return f"""\
<!DOCTYPE html>
<html lang="fr">
<body style="margin:0;background:#f4f6f8;font-family:Segoe UI,Arial,sans-serif;color:#2c3e50;">
  <div style="max-width:600px;margin:24px auto;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.08);">
    <div style="background:#E74C3C;color:#fff;padding:20px 24px;">
      <h1 style="margin:0;font-size:20px;">ALERTE FutureKawa — {pays_label.upper()}</h1>
      <p style="margin:6px 0 0;opacity:.9;font-size:13px;">Relevé capteur hors plage — {stamp}</p>
    </div>
    <div style="padding:24px;">
      <p style="margin:0 0 16px;">
        Un relevé <strong>hors seuil</strong> a été détecté sur l'entrepôt
        <strong>{entrepot}</strong> ({pays_label} — <code>{pays_slug.upper()}</code>).
      </p>
      <table style="width:100%;border-collapse:collapse;background:#fafbfc;border-radius:8px;">
        <tr style="background:#ecf0f1;">
          <th style="text-align:left;padding:8px 12px;">Mesure</th>
          <th style="text-align:left;padding:8px 12px;">Valeur</th>
          <th style="text-align:left;padding:8px 12px;">Seuils</th>
          <th style="text-align:left;padding:8px 12px;">Statut</th>
        </tr>
        {_status_row("Température", temperature, " °C", temp_min, temp_max)}
        {_status_row("Humidité", humidity, " %", hum_min, hum_max)}
      </table>
      <p style="margin:20px 0 8px;font-size:13px;color:#7f8c8d;">Lot concerné : <code>{lot_id[:8]}…</code></p>
      <a href="{DASHBOARD_URL}"
         style="display:inline-block;margin-top:12px;background:#2c3e50;color:#fff;text-decoration:none;
                padding:12px 20px;border-radius:8px;font-weight:600;">
        Ouvrir le tableau de bord
      </a>
    </div>
    <div style="padding:16px 24px;background:#f4f6f8;font-size:12px;color:#95a5a6;">
      FutureKawa IoT Monitoring • Seuils configurables sur /config/capteurs
    </div>
  </div>
</body>
</html>"""


def _build_condition_text(
    *,
    pays_label: str,
    entrepot: str,
    lot_id: str,
    temperature: float,
    humidity: float,
    temp_min: float,
    temp_max: float,
    hum_min: float,
    hum_max: float,
) -> str:
    stamp = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M:%S UTC")
    return (
        f"ALERTE FutureKawa — {pays_label.upper()}\n"
        f"{stamp}\n\n"
        f"Entrepôt : {entrepot}\n"
        f"Lot      : {lot_id[:8]}...\n\n"
        f"Température : {temperature:.1f} °C (plage {temp_min:.1f} - {temp_max:.1f})\n"
        f"Humidité   : {humidity:.1f} % (plage {hum_min:.1f} - {hum_max:.1f})\n\n"
        f"Tableau de bord : {DASHBOARD_URL}\n"
    )


def _send(config: GmailConfig, message: EmailMessage, context: str) -> bool:
    """Ouvre une session SMTP Gmail (STARTTLS) et envoie le message."""
    ssl_context = ssl.create_default_context()
    try:
        with smtplib.SMTP(config.host, config.port, timeout=15) as server:
            server.ehlo()
            server.starttls(context=ssl_context)
            server.ehlo()
            server.login(config.user, config.app_password)
            server.send_message(message)
        logger.info("Alerte e-mail envoyée (%s) → %s", context, ", ".join(config.recipients))
        return True
    except smtplib.SMTPAuthenticationError:
        logger.error(
            "Auth Gmail refusée — vérifiez GMAIL_ALERT_USER / GMAIL_APP_PASSWORD "
            "(mot de passe d'application, pas le mot de passe du compte)."
        )
        return False
    except (smtplib.SMTPException, OSError) as exc:
        logger.warning("Échec envoi e-mail (%s) : %s", context, exc)
        return False


def _new_message(config: GmailConfig, subject: str) -> EmailMessage:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = formataddr((config.sender_name, config.user))
    msg["To"] = ", ".join(config.recipients)
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain="futurekawa.local")
    return msg


def send_condition_email(
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
    config: GmailConfig | None = None,
) -> bool:
    """Envoie l'alerte conditions par e-mail. Retourne False si non configuré."""
    config = config or GmailConfig.from_env()
    if not config.is_configured:
        logger.debug("Gmail non configuré (GMAIL_* absents) — alerte e-mail ignorée")
        return False

    subject = f"[FutureKawa] Alerte {pays_label} — {entrepot} hors seuil"
    msg = _new_message(config, subject)
    msg.set_content(
        _build_condition_text(
            pays_label=pays_label,
            entrepot=entrepot,
            lot_id=lot_id,
            temperature=temperature,
            humidity=humidity,
            temp_min=temp_min,
            temp_max=temp_max,
            hum_min=hum_min,
            hum_max=hum_max,
        )
    )
    msg.add_alternative(
        _build_condition_html(
            pays_label=pays_label,
            pays_slug=pays_slug,
            entrepot=entrepot,
            lot_id=lot_id,
            temperature=temperature,
            humidity=humidity,
            temp_min=temp_min,
            temp_max=temp_max,
            hum_min=hum_min,
            hum_max=hum_max,
        ),
        subtype="html",
    )
    return _send(config, msg, f"{pays_slug}/condition")


def send_test_email(config: GmailConfig | None = None) -> bool:
    """Envoie un e-mail de test pour valider la configuration SMTP Gmail."""
    config = config or GmailConfig.from_env()
    if not config.is_configured:
        logger.error(
            "Impossible d'envoyer le test : renseignez GMAIL_ALERT_USER, "
            "GMAIL_APP_PASSWORD et ALERT_EMAIL_TO dans .env"
        )
        return False
    stamp = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M:%S UTC")
    msg = _new_message(config, "[FutureKawa] Test de la chaîne d'alerte e-mail")
    msg.set_content(
        f"Test d'envoi FutureKawa — {stamp}\n\n"
        f"Si vous recevez cet e-mail, la configuration Gmail (SMTP STARTTLS) est opérationnelle."
    )
    msg.add_alternative(
        f"""\
<html><body style="font-family:Segoe UI,Arial,sans-serif;">
  <h2 style="color:#2c3e50;">Test FutureKawa réussi ✅</h2>
  <p>Envoyé le <strong>{stamp}</strong> depuis <code>{config.user}</code>.</p>
  <p style="color:#7f8c8d;">La chaîne d'alerte e-mail est opérationnelle.</p>
</body></html>""",
        subtype="html",
    )
    return _send(config, msg, "test")


def _demo_condition() -> bool:
    """Envoie une alerte conditions factice (valeurs de démonstration)."""
    return send_condition_email(
        pays_slug="bresil",
        pays_label="Bresil",
        entrepot="Entrepot Santos",
        lot_id="a1b2c3d4-0000-1111-2222-333344445555",
        temperature=31.4,
        humidity=72.0,
        temp_min=18.0,
        temp_max=24.0,
        hum_min=50.0,
        hum_max=65.0,
    )


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description="Alertes e-mail Gmail — FutureKawa")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--test", action="store_true", help="Envoyer un e-mail de test")
    group.add_argument(
        "--demo-condition",
        action="store_true",
        help="Envoyer une alerte conditions factice",
    )
    args = parser.parse_args()

    ok = send_test_email() if args.test else _demo_condition()
    if ok:
        print("E-mail envoyé.")
        return 0
    print("Envoi échoué (voir logs / configuration .env).", flush=True)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
