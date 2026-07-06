"""Tests unitaires pour la construction d'embeds Discord (siège)."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "siege"))

pytestmark = pytest.mark.unit

from api.services.discord_embed import (
    build_condition_embed,
    build_message_embed,
    build_test_webhook_embed,
    webhook_payload,
)


def test_build_condition_embed_structure():
    embed = build_condition_embed(
        pays_slug="bresil",
        pays_label="Brésil",
        entrepot="Entrepot SP",
        lot_id="abc12345-6789",
        temperature=35.0,
        humidity=40.0,
        temp_min=26.0,
        temp_max=32.0,
        hum_min=53.0,
        hum_max=57.0,
    )
    assert "BRÉSIL" in embed["title"]
    assert embed["color"] == 0xE74C3C
    assert len(embed["fields"]) == 5
    temp_field = embed["fields"][3]["value"]
    assert "HORS SEUIL" in temp_field
    hum_field = embed["fields"][4]["value"]
    assert "HORS SEUIL" in hum_field
    assert "timestamp" in embed


def test_build_condition_embed_conforme_readings():
    embed = build_condition_embed(
        pays_slug="colombie",
        pays_label="Colombie",
        entrepot="Entrepot BO",
        lot_id="lot-001",
        temperature=26.0,
        humidity=80.0,
        temp_min=23.0,
        temp_max=29.0,
        hum_min=78.0,
        hum_max=82.0,
    )
    temp_field = embed["fields"][3]["value"]
    hum_field = embed["fields"][4]["value"]
    assert "CONFORME" in temp_field
    assert "CONFORME" in hum_field


def test_build_test_webhook_embed():
    embed = build_test_webhook_embed(triggered_by="admin_siege", environment="local")
    assert "Validation webhook Discord" in embed["title"]
    assert embed["color"] == 0x2ECC71
    assert "admin_siege" in embed["fields"][0]["value"]
    assert embed["fields"][1]["value"] == "`local`"


@pytest.mark.parametrize(
    "alert_type,expected_color",
    [
        ("condition", 0xE74C3C),
        ("peremption", 0xE67E22),
        ("connection", 0xF1C40F),
        ("test", 0x3498DB),
    ],
)
def test_build_message_embed_colors(alert_type, expected_color):
    embed = build_message_embed("message test", "bresil", alert_type)
    assert embed["color"] == expected_color
    assert "BRESIL" in embed["title"]


def test_build_message_embed_converts_bullet_lines():
    text = "- ligne un\n- ligne deux\nTexte libre"
    embed = build_message_embed(text, "equateur", "connection")
    assert "• ligne un" in embed["description"]
    assert "• ligne deux" in embed["description"]
    assert "Texte libre" in embed["description"]


def test_webhook_payload_wraps_embed():
    embed = {"title": "test"}
    assert webhook_payload(embed) == {"embeds": [embed]}
