from datetime import datetime
from types import SimpleNamespace

import pytest

pytestmark = pytest.mark.unit


def _sort_fifo(lots):
    """Reproduit order_by(Lot.date_stockage.asc()) de l'API lots."""
    return sorted(lots, key=lambda lot: lot.date_stockage)


def test_fifo_sort_oldest_first():
    lots = [
        SimpleNamespace(id="lot-c", date_stockage=datetime(2025, 3, 1)),
        SimpleNamespace(id="lot-a", date_stockage=datetime(2025, 1, 1)),
        SimpleNamespace(id="lot-b", date_stockage=datetime(2025, 2, 1)),
    ]

    ordered = _sort_fifo(lots)

    assert [lot.id for lot in ordered] == ["lot-a", "lot-b", "lot-c"]
    dates = [lot.date_stockage for lot in ordered]
    assert dates == sorted(dates)


def test_fifo_preserves_order_when_dates_equal():
    same_date = datetime(2025, 6, 15)
    lots = [
        SimpleNamespace(id="lot-1", date_stockage=same_date),
        SimpleNamespace(id="lot-2", date_stockage=same_date),
    ]

    ordered = _sort_fifo(lots)

    assert len(ordered) == 2
    assert ordered[0].date_stockage == same_date


def test_fifo_empty_list():
    assert _sort_fifo([]) == []


def test_fifo_single_lot():
    lot = SimpleNamespace(id="solo", date_stockage=datetime(2025, 1, 1))
    assert _sort_fifo([lot]) == [lot]
