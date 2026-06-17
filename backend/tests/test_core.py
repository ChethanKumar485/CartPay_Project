"""
CartPay — Backend Unit Tests
Run: pytest tests/ -v
"""

import pytest
from app.services.weight    import verify_weight, cumulative_verify, bag_size_for
from app.services.inventory import get_item_by_barcode, search_items
from app.models.schemas     import BagSize


# ─── Weight verification ────────────────────────────────────────────────────

def test_weight_ok():
    assert verify_weight(expected=1000, measured=1020, tolerance_pct=5) is True

def test_weight_over_tolerance():
    assert verify_weight(expected=1000, measured=1200, tolerance_pct=5) is False

def test_weight_exactly_at_boundary():
    assert verify_weight(expected=1000, measured=1050, tolerance_pct=5) is True   # 5% = 50 g

def test_cumulative_ok():
    r = cumulative_verify(5000, 5080)
    assert r["ok"] is True

def test_cumulative_mismatch():
    r = cumulative_verify(1000, 1600)
    assert r["ok"] is False

def test_bag_size_small():
    assert bag_size_for(1500) == BagSize.SMALL

def test_bag_size_medium():
    assert bag_size_for(3000) == BagSize.MEDIUM

def test_bag_size_large():
    assert bag_size_for(7000) == BagSize.LARGE

def test_bag_size_jumbo():
    assert bag_size_for(15000) == BagSize.JUMBO


# ─── Inventory ──────────────────────────────────────────────────────────────

def test_lookup_known_barcode():
    item = get_item_by_barcode("8901030123456")
    assert item is not None
    assert item.name == "Basmati Rice 1kg"

def test_lookup_unknown_barcode():
    assert get_item_by_barcode("0000000000000") is None

def test_search_returns_results():
    results = search_items("rice")
    assert len(results) >= 1

def test_search_case_insensitive():
    r1 = search_items("RICE")
    r2 = search_items("rice")
    assert len(r1) == len(r2)

def test_effective_price_discount():
    item = get_item_by_barcode("8901030123461")   # Fresh Curd, 10% off
    assert item.effective_price < item.price
