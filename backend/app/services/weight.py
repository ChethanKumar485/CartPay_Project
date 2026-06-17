"""
CartPay — Weight Verification Service
Compares measured basket weight vs. expected to detect item mismatches.
"""

from app.models.schemas import BagSize

BAG_THRESHOLDS: list[tuple[float, BagSize]] = [
    (2000,       BagSize.SMALL),
    (5000,       BagSize.MEDIUM),
    (10000,      BagSize.LARGE),
    (float("inf"), BagSize.JUMBO),
]


def verify_weight(expected: float, measured: float, tolerance_pct: float = 5.0) -> bool:
    """Return True if measured weight is within tolerance of expected."""
    band = max(30, expected * (tolerance_pct / 100))
    return abs(measured - expected) <= band


def cumulative_verify(
    expected_total: float,
    measured_total: float,
    global_tolerance_pct: float = 3.0,
) -> dict:
    """
    Check the running basket total weight.
    Uses a larger absolute floor (40 g) to avoid false alarms from sensor noise.
    """
    band = max(40, expected_total * (global_tolerance_pct / 100))
    diff = abs(measured_total - expected_total)
    ok   = diff <= band
    return {
        "ok":        ok,
        "expected":  round(expected_total, 1),
        "measured":  round(measured_total, 1),
        "diff":      round(diff, 1),
        "tolerance": round(band, 1),
    }


def bag_size_for(weight_grams: float) -> BagSize:
    for threshold, size in BAG_THRESHOLDS:
        if weight_grams <= threshold:
            return size
    return BagSize.JUMBO
