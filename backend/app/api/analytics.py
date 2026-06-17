"""CartPay — Analytics Router"""
from fastapi import APIRouter
from app.models.schemas import DashboardStats
import random

router = APIRouter()


@router.get("/dashboard", response_model=DashboardStats)
def dashboard():
    """Returns simulated live store statistics. Connect to real DB in production."""
    return DashboardStats(
        active_carts        = random.randint(3, 18),
        paid_today          = random.randint(40, 250),
        revenue_today       = round(random.uniform(12000, 85000), 2),
        avg_checkout_time_s = round(random.uniform(95, 210), 1),
        mismatch_alerts     = random.randint(0, 4),
        top_items           = [
            {"name": "Basmati Rice 1kg",    "units": random.randint(20, 80)},
            {"name": "Toned Milk 1L",       "units": random.randint(15, 70)},
            {"name": "Detergent Powder 1kg","units": random.randint(10, 55)},
        ],
    )
