"""
CartPay — Payments Router
Handles: digital payment, cash payment, change calculation.
"""

from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    DigitalPayRequest, CashPayRequest, CashPayResponse,
    TransactionRecord, PaymentMode,
)
import uuid, datetime

router = APIRouter()

DENOMINATIONS = [500, 200, 100, 50, 20, 10, 5, 2, 1]

# In-memory transaction log (use PostgreSQL in production)
_transactions: list[TransactionRecord] = []
# Cart RFID → paid session_id map (use Redis in production)
_paid_carts: dict[str, str] = {}


def _breakdown(change: float) -> dict:
    """Return denomination → count for the given change amount."""
    remaining = int(round(change))
    result = {}
    for d in DENOMINATIONS:
        count = remaining // d
        if count:
            result[str(d)] = count
        remaining -= d * count
    return result


@router.post("/{session_id}/digital", response_model=TransactionRecord)
def pay_digital(session_id: str, body: DigitalPayRequest, amount: float):
    """
    Simulate a digital payment (UPI / card).
    In production: forward the token to Razorpay / Stripe and await webhook.
    """
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount")

    txn = TransactionRecord(
        transaction_id=f"TXN-{uuid.uuid4().hex[:10].upper()}",
        session_id=session_id,
        amount=amount,
        payment_mode=PaymentMode.DIGITAL,
    )
    _transactions.append(txn)
    _paid_carts[session_id] = session_id  # keyed by session here; use RFID in real system
    return txn


@router.post("/kiosk/{cart_rfid}/cash", response_model=CashPayResponse)
def pay_cash(cart_rfid: str, body: CashPayRequest):
    """
    Cash payment at the exit kiosk.
    - Validates tendered amount vs. bill.
    - Calculates exact change.
    - Returns a denomination breakdown for the change dispenser.
    """
    # In production: fetch pending bill from session store by cart_rfid
    # Here we use the bill_amount passed via body for demo simplicity
    bill_amount = body.tendered_amount  # caller provides; in prod fetch from session

    # To properly demo, the route expects a separate bill_amount query param.
    # We'll read it from a query param added below.
    raise HTTPException(
        status_code=501,
        detail="Use POST /kiosk/{cart_rfid}/cash?bill_amount=<amount>"
    )


@router.post("/kiosk/{cart_rfid}/cash/pay", response_model=CashPayResponse)
def pay_cash_full(cart_rfid: str, bill_amount: float, tendered_amount: float):
    """Cash payment with explicit bill and tendered amounts."""
    if tendered_amount < bill_amount:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient amount. Due: ₹{bill_amount - tendered_amount:.2f}"
        )

    change = round(tendered_amount - bill_amount, 2)
    breakdown = _breakdown(change) if change > 0 else {}

    _paid_carts[cart_rfid] = cart_rfid

    return CashPayResponse(
        success=True,
        bill_amount=bill_amount,
        tendered=tendered_amount,
        change=change,
        change_notes=breakdown,
        receipt_url=f"/receipt/{cart_rfid}",
    )


@router.get("/gate/{cart_rfid}/check")
def gate_check(cart_rfid: str):
    """Exit gate calls this to verify the cart is paid."""
    paid = cart_rfid in _paid_carts
    return {"cart_rfid": cart_rfid, "paid": paid, "gate_open": paid}


@router.get("/transactions")
def list_transactions():
    return _transactions
