"""Genere un PDF fictif representant l'e-mail d'alerte FutureKawa.

Reprend la mise en page et les donnees de l'embed Discord (alerte conditions)
pour illustrer le rendu du canal e-mail Gmail (voir scripts/email_alert.py).
C'est un livrable de demonstration : aucune connexion reseau / BDD.

Usage :
  python scripts/generate_alert_email_pdf.py
  python scripts/generate_alert_email_pdf.py --output docs/exemples/alerte.pdf
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from pathlib import Path

from fpdf import FPDF

REPO_ROOT = Path(__file__).resolve().parents[1]

# Palette alignee sur l'embed Discord (discord_embed.py)
RED = (231, 76, 60)        # #E74C3C - hors seuil / bandeau alerte
GREEN = (46, 204, 113)     # #2ECC71 - conforme
DARK = (44, 62, 80)        # #2c3e50 - texte principal / bouton
GREY = (127, 140, 141)     # #7f8c8d - texte secondaire
LIGHT = (236, 240, 241)    # #ecf0f1 - entetes de tableau
PANEL = (250, 251, 252)    # #fafbfc - fond tableau
PAGE_BG = (244, 246, 248)  # #f4f6f8 - fond de page
WHITE = (255, 255, 255)
MAILBAR = (52, 73, 94)     # bandeau client mail


@dataclass
class AlertData:
    """Donnees de l'alerte (valeurs par defaut = capture Discord fournie)."""

    pays_label: str = "Bresil"
    pays_code: str = "BRESIL"
    entrepot: str = "Entrepot BR-1"
    lot_id: str = "390a7ec8-1f4d-42aa-9c11-0b7e5d9a2f31"
    temperature: float = 29.8
    humidity: float = 31.0
    temp_min: float = 20.0
    temp_max: float = 25.0
    hum_min: float = 53.0
    hum_max: float = 57.0
    horodatage: str = "21/06/2026 15:32"
    sender: str = "FutureKawa IoT <futurekawa.alertes@gmail.com>"
    recipients: str = "supervision@futurekawa.com, ops@futurekawa.com"

    @property
    def subject(self) -> str:
        return f"[FutureKawa] Alerte {self.pays_label} - {self.entrepot} hors seuil"


class AlertPDF(FPDF):
    """Document A4 unicode-safe (police Arial si dispo, sinon Helvetica)."""

    def __init__(self) -> None:
        super().__init__(orientation="P", unit="mm", format="A4")
        self.unicode = self._register_unicode_font()
        self.set_auto_page_break(auto=False)

    def _register_unicode_font(self) -> bool:
        for name, regular, bold in (
            ("mail", r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\arialbd.ttf"),
        ):
            if Path(regular).exists() and Path(bold).exists():
                self.add_font(name, "", regular)
                self.add_font(name, "B", bold)
                self.font_family_name = name
                return True
        self.font_family_name = "Helvetica"
        return False

    def txt(self, s: str) -> str:
        """Rend le texte compatible avec la police (fallback latin-1)."""
        if self.unicode:
            return s
        replacements = {"\u2014": "-", "\u2022": "*", "\u2026": "...", "\u00b0": "deg", "\u00e9": "e"}
        for bad, good in replacements.items():
            s = s.replace(bad, good)
        return s

    def font(self, style: str = "", size: float = 10) -> None:
        self.set_font(self.font_family_name, style, size)


def _fill(pdf: AlertPDF, rgb: tuple[int, int, int]) -> None:
    pdf.set_fill_color(*rgb)


def _text_color(pdf: AlertPDF, rgb: tuple[int, int, int]) -> None:
    pdf.set_text_color(*rgb)


def _status_cell(pdf: AlertPDF, x: float, y: float, w: float, value: float, lo: float, hi: float) -> None:
    ok = lo <= value <= hi
    _text_color(pdf, GREEN if ok else RED)
    pdf.font("B", 9)
    pdf.set_xy(x, y)
    pdf.cell(w, 6, pdf.txt("CONFORME" if ok else "HORS SEUIL"))


def _metric_row(pdf: AlertPDF, y: float, label: str, value: float, unit: str, lo: float, hi: float) -> None:
    left = 22.0
    _text_color(pdf, DARK)
    pdf.font("B", 10)
    pdf.set_xy(left, y)
    pdf.cell(45, 6, pdf.txt(label))

    pdf.font("", 10)
    pdf.set_xy(left + 45, y)
    pdf.cell(30, 6, f"{value:.1f}{unit}")

    _text_color(pdf, GREY)
    pdf.font("", 9)
    pdf.set_xy(left + 78, y)
    pdf.cell(50, 6, pdf.txt(f"plage {lo:.1f} - {hi:.1f}{unit}"))

    _status_cell(pdf, left + 132, y, 35, value, lo, hi)


def build_pdf(data: AlertData, output: Path) -> Path:
    pdf = AlertPDF()
    pdf.add_page()

    # Fond de page
    _fill(pdf, PAGE_BG)
    pdf.rect(0, 0, 210, 297, style="F")

    card_x, card_w = 20.0, 170.0
    top = 18.0

    # --- Bandeau client mail ---
    _fill(pdf, MAILBAR)
    pdf.rect(card_x, top, card_w, 12, style="F")
    _text_color(pdf, WHITE)
    pdf.font("B", 11)
    pdf.set_xy(card_x + 6, top + 3.5)
    pdf.cell(0, 5, pdf.txt("Boite de reception - Alerte automatique"))

    # --- En-tetes du message ---
    header_y = top + 12
    _fill(pdf, WHITE)
    pdf.rect(card_x, header_y, card_w, 26, style="F")
    meta = [
        ("De :", data.sender),
        ("A :", data.recipients),
        ("Objet :", data.subject),
        ("Date :", f"{data.horodatage} UTC"),
    ]
    my = header_y + 3
    for label, value in meta:
        _text_color(pdf, GREY)
        pdf.font("B", 8.5)
        pdf.set_xy(card_x + 6, my)
        pdf.cell(16, 5, pdf.txt(label))
        _text_color(pdf, DARK)
        pdf.font("", 8.5)
        pdf.set_xy(card_x + 24, my)
        pdf.cell(card_w - 30, 5, pdf.txt(value))
        my += 5.5

    # --- Bandeau alerte (rouge, comme l'embed Discord) ---
    alert_y = header_y + 26
    _fill(pdf, RED)
    pdf.rect(card_x, alert_y, card_w, 18, style="F")
    _text_color(pdf, WHITE)
    pdf.font("B", 15)
    pdf.set_xy(card_x + 8, alert_y + 3)
    pdf.cell(0, 7, pdf.txt(f"ALERTE FutureKawa - {data.pays_code}"))
    pdf.font("", 9)
    pdf.set_xy(card_x + 8, alert_y + 11)
    pdf.cell(0, 4, pdf.txt(f"Releve capteur hors plage - {data.horodatage} UTC"))

    # --- Corps ---
    body_y = alert_y + 18
    body_h = 96.0
    _fill(pdf, WHITE)
    pdf.rect(card_x, body_y, card_w, body_h, style="F")

    _text_color(pdf, DARK)
    pdf.font("", 10)
    pdf.set_xy(22, body_y + 6)
    pdf.multi_cell(
        card_w - 4,
        5.5,
        pdf.txt(
            f"Un releve HORS SEUIL a ete detecte sur l'entrepot {data.entrepot} "
            f"({data.pays_label} - {data.pays_code})."
        ),
    )

    # Ligne Pays / Entrepot / Lot
    info_y = body_y + 22
    cols = [
        ("Pays", f"{data.pays_label} ({data.pays_code})"),
        ("Entrepot", data.entrepot),
        ("Lot", f"{data.lot_id[:8]}..."),
    ]
    cx = 22.0
    for title, value in cols:
        _text_color(pdf, GREY)
        pdf.font("B", 8)
        pdf.set_xy(cx, info_y)
        pdf.cell(52, 4, pdf.txt(title.upper()))
        _text_color(pdf, DARK)
        pdf.font("B", 10)
        pdf.set_xy(cx, info_y + 5)
        pdf.cell(52, 5, pdf.txt(value))
        cx += 55

    # Tableau mesures
    tbl_y = info_y + 18
    _fill(pdf, LIGHT)
    pdf.rect(20, tbl_y, card_w, 8, style="F")
    _text_color(pdf, DARK)
    pdf.font("B", 9)
    for label, dx, w in (("MESURE", 2, 45), ("VALEUR", 45, 30), ("SEUILS", 78, 50), ("STATUT", 132, 35)):
        pdf.set_xy(20 + dx, tbl_y + 1.5)
        pdf.cell(w, 5, pdf.txt(label))

    _fill(pdf, PANEL)
    pdf.rect(20, tbl_y + 8, card_w, 16, style="F")
    _metric_row(pdf, tbl_y + 10, "Temperature", data.temperature, " \u00b0C", data.temp_min, data.temp_max)
    _metric_row(pdf, tbl_y + 18, "Humidite", data.humidity, " %", data.hum_min, data.hum_max)

    # Bouton
    btn_y = tbl_y + 34
    _fill(pdf, DARK)
    pdf.rect(22, btn_y, 62, 11, style="F")
    _text_color(pdf, WHITE)
    pdf.font("B", 10)
    pdf.set_xy(22, btn_y + 3)
    pdf.cell(62, 5, pdf.txt("Ouvrir le tableau de bord"), align="C")

    _text_color(pdf, GREY)
    pdf.font("", 8)
    pdf.set_xy(22, btn_y + 15)
    pdf.cell(0, 4, pdf.txt("https://mspr2-master-front.onrender.com/alertes"))

    # --- Pied ---
    footer_y = body_y + body_h
    _fill(pdf, PAGE_BG)
    pdf.rect(card_x, footer_y, card_w, 12, style="F")
    _text_color(pdf, GREY)
    pdf.font("", 8)
    pdf.set_xy(card_x + 6, footer_y + 4)
    pdf.cell(
        0,
        4,
        pdf.txt("FutureKawa IoT Monitoring \u2022 Seuils configurables sur /config/capteurs"),
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(output))
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Genere un PDF fictif d'alerte e-mail FutureKawa")
    parser.add_argument(
        "--output",
        default=str(REPO_ROOT / "docs" / "exemples" / "alerte_mail_futurekawa.pdf"),
        help="Chemin du PDF de sortie",
    )
    args = parser.parse_args()

    path = build_pdf(AlertData(), Path(args.output))
    print(f"PDF genere : {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
