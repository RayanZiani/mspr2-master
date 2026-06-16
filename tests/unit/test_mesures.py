from datetime import datetime
from types import SimpleNamespace

import pytest

pytestmark = pytest.mark.unit


def _filter_mesures(mesures, lot_id=None):
    """Reproduit le filtre lot_id de list_mesures (routes/mesures.py)."""
    if not lot_id:
        return mesures
    return [mesure for mesure in mesures if mesure.lot_id == lot_id]


def _sort_mesures_desc(mesures):
    """Reproduit order_by(Mesure.timestamp.desc())."""
    return sorted(mesures, key=lambda m: m.timestamp, reverse=True)


def test_filter_mesures_by_lot_id():
    mesures = [
        SimpleNamespace(lot_id="lot-a", temperature=29.0, humidity=55.0, timestamp=datetime(2025, 1, 1)),
        SimpleNamespace(lot_id="lot-b", temperature=30.0, humidity=56.0, timestamp=datetime(2025, 1, 2)),
        SimpleNamespace(lot_id="lot-a", temperature=28.5, humidity=54.0, timestamp=datetime(2025, 1, 3)),
    ]

    filtered = _filter_mesures(mesures, lot_id="lot-a")

    assert len(filtered) == 2
    assert all(m.lot_id == "lot-a" for m in filtered)


def test_filter_unknown_lot_returns_empty():
    mesures = [
        SimpleNamespace(lot_id="lot-a", timestamp=datetime(2025, 1, 1)),
    ]
    assert _filter_mesures(mesures, lot_id="unknown") == []


def test_list_mesures_without_filter_returns_all():
    mesures = [
        SimpleNamespace(lot_id="lot-a", timestamp=datetime(2025, 1, 1)),
        SimpleNamespace(lot_id="lot-b", timestamp=datetime(2025, 1, 2)),
    ]

    assert len(_filter_mesures(mesures)) == 2


def test_mesures_sorted_newest_first():
    mesures = [
        SimpleNamespace(lot_id="lot-a", timestamp=datetime(2025, 1, 1)),
        SimpleNamespace(lot_id="lot-a", timestamp=datetime(2025, 6, 1)),
        SimpleNamespace(lot_id="lot-a", timestamp=datetime(2025, 3, 1)),
    ]

    ordered = _sort_mesures_desc(mesures)

    assert ordered[0].timestamp == datetime(2025, 6, 1)
    assert ordered[-1].timestamp == datetime(2025, 1, 1)
