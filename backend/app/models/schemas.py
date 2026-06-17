"""
CartPay — Pydantic Models
"""

from __future__ import annotations
from datetime import datetime, date
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


# ─── Enums ────────────────────────────────────────────────────────────────────

class SessionStatus(str, Enum):
    ACTIVE    = "active"
    PAID      = "paid"
    ABANDONED = "abandoned"

class PaymentMode(str, Enum):
    DIGITAL = "digital"
    CASH    = "cash"

class AlertType(str, Enum):
    MISMATCH    = "mismatch"
    THEFT       = "theft"
    LOW_BATTERY = "low_battery"
    EXPIRED     = "expired"

class BagSize(str, Enum):
    SMALL  = "Small bag"
    MEDIUM = "Medium bag"
    LARGE  = "Large bag"
    JUMBO  = "Jumbo bag (or 2 bags)"


# ─── Item ─────────────────────────────────────────────────────────────────────

class Item(BaseModel):
    item_id:          str
    barcode:          str
    name:             str
    category:         str
    price:            float
    reference_weight: float          # grams
    tolerance_pct:    float = 5.0   # ±%
    expiry_date:      Optional[date]
    image_url:        Optional[str]
    discount_pct:     float = 0.0

    @property
    def effective_price(self) -> float:
        return round(self.price * (1 - self.discount_pct / 100), 2)

    @property
    def days_until_expiry(self) -> Optional[int]:
        if self.expiry_date is None:
            return None
        return (self.expiry_date - date.today()).days


# ─── Session ──────────────────────────────────────────────────────────────────

class ScanEvent(BaseModel):
    barcode:         str
    expected_weight: float
    measured_weight: float
    timestamp:       datetime = Field(default_factory=datetime.utcnow)
    mismatch:        bool = False

class SessionItem(BaseModel):
    barcode:    str
    item_name:  str
    quantity:   int
    unit_price: float
    line_total: float

class SessionState(BaseModel):
    session_id:    str
    cart_id:       str
    user_id:       Optional[str]
    status:        SessionStatus = SessionStatus.ACTIVE
    scan_events:   List[ScanEvent] = []
    items:         List[SessionItem] = []
    subtotal:      float = 0.0
    total_weight:  float = 0.0
    bag_size:      Optional[BagSize]
    mismatch_flag: bool = False
    start_time:    datetime = Field(default_factory=datetime.utcnow)
    end_time:      Optional[datetime]

class ScanRequest(BaseModel):
    barcode:         str
    measured_weight: float

class RemoveItemRequest(BaseModel):
    barcode: str

class WeightCheckRequest(BaseModel):
    current_total_weight: float


# ─── Payment ──────────────────────────────────────────────────────────────────

class DigitalPayRequest(BaseModel):
    gateway: str = "razorpay"    # or "upi", "stripe"
    token:   Optional[str]       # tokenised card / UPI VPA

class CashPayRequest(BaseModel):
    cart_rfid:      str
    tendered_amount: float

class CashPayResponse(BaseModel):
    success:       bool
    bill_amount:   float
    tendered:      float
    change:        float
    change_notes:  dict          # denomination → count breakdown
    receipt_url:   Optional[str]

class TransactionRecord(BaseModel):
    transaction_id: str
    session_id:     str
    amount:         float
    payment_mode:   PaymentMode
    change_given:   float = 0.0
    status:         str = "success"
    timestamp:      datetime = Field(default_factory=datetime.utcnow)


# ─── Alert ────────────────────────────────────────────────────────────────────

class Alert(BaseModel):
    alert_id:   str
    session_id: str
    cart_id:    str
    alert_type: AlertType
    detail:     str
    resolved:   bool = False
    timestamp:  datetime = Field(default_factory=datetime.utcnow)


# ─── Analytics ────────────────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    active_carts:       int
    paid_today:         int
    revenue_today:      float
    avg_checkout_time_s: float
    mismatch_alerts:    int
    top_items:          List[dict]
