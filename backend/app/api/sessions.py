"""
CartPay — Sessions Router
Handles: start session, scan item, remove item, weight check, checkout.
"""

from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    SessionState, ScanRequest, RemoveItemRequest,
    WeightCheckRequest, BagSize, ScanEvent, SessionItem, SessionStatus,
)
from app.services.inventory import get_item_by_barcode
from app.services.weight    import verify_weight, bag_size_for
import uuid, datetime

router = APIRouter()

# In-memory session store (replace with Redis/DB in production)
_sessions: dict[str, SessionState] = {}


def _get_session(session_id: str) -> SessionState:
    s = _sessions.get(session_id)
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    if s.status != SessionStatus.ACTIVE:
        raise HTTPException(status_code=409, detail=f"Session is {s.status}")
    return s


@router.post("/start", response_model=SessionState, status_code=201)
def start_session(cart_id: str, user_id: str | None = None):
    """Assign a cart to a new shopping session."""
    sid = "SID-" + uuid.uuid4().hex[:8].upper()
    session = SessionState(session_id=sid, cart_id=cart_id, user_id=user_id)
    _sessions[sid] = session
    return session


@router.post("/{session_id}/scan", response_model=SessionState)
def scan_item(session_id: str, body: ScanRequest):
    """Register a scanned barcode and run weight-check against expected weight."""
    session = _get_session(session_id)
    item = get_item_by_barcode(body.barcode)
    if not item:
        raise HTTPException(status_code=404, detail=f"Barcode {body.barcode} not found in inventory")

    mismatch = not verify_weight(
        expected=item.reference_weight,
        measured=body.measured_weight,
        tolerance_pct=item.tolerance_pct,
    )

    event = ScanEvent(
        barcode=body.barcode,
        expected_weight=item.reference_weight,
        measured_weight=body.measured_weight,
        mismatch=mismatch,
    )
    session.scan_events.append(event)

    # Update item groupings
    existing = next((i for i in session.items if i.barcode == body.barcode), None)
    if existing:
        existing.quantity += 1
        existing.line_total = round(existing.unit_price * existing.quantity, 2)
    else:
        session.items.append(SessionItem(
            barcode=body.barcode,
            item_name=item.name,
            quantity=1,
            unit_price=item.effective_price,
            line_total=item.effective_price,
        ))

    session.subtotal     = round(sum(i.line_total for i in session.items), 2)
    session.total_weight = round(sum(e.measured_weight for e in session.scan_events), 2)
    session.bag_size     = bag_size_for(session.total_weight)
    session.mismatch_flag = mismatch

    return session


@router.delete("/{session_id}/item", response_model=SessionState)
def remove_item(session_id: str, body: RemoveItemRequest):
    """Remove one unit of a scanned item from the session."""
    session = _get_session(session_id)

    # Remove the last scan event for this barcode
    for i in reversed(range(len(session.scan_events))):
        if session.scan_events[i].barcode == body.barcode:
            session.scan_events.pop(i)
            break
    else:
        raise HTTPException(status_code=404, detail="Item not in cart")

    for si in session.items:
        if si.barcode == body.barcode:
            si.quantity -= 1
            si.line_total = round(si.unit_price * si.quantity, 2)
            if si.quantity <= 0:
                session.items.remove(si)
            break

    session.subtotal     = round(sum(i.line_total for i in session.items), 2)
    session.total_weight = round(sum(e.measured_weight for e in session.scan_events), 2)
    session.bag_size     = bag_size_for(session.total_weight) if session.total_weight > 0 else None
    session.mismatch_flag = any(e.mismatch for e in session.scan_events)

    return session


@router.post("/{session_id}/verify-weight")
def verify_weight_check(session_id: str, body: WeightCheckRequest):
    """
    Called continuously by the cart firmware to validate total basket weight.
    Returns a mismatch flag and expected vs. measured totals.
    """
    session = _get_session(session_id)
    expected = sum(e.expected_weight for e in session.scan_events)
    tolerance = max(40, expected * 0.03)
    diff = abs(body.current_total_weight - expected)
    ok = diff <= tolerance
    return {
        "ok":       ok,
        "expected": expected,
        "measured": body.current_total_weight,
        "diff":     round(diff, 1),
        "tolerance": round(tolerance, 1),
    }


@router.get("/{session_id}/total", response_model=SessionState)
def get_total(session_id: str):
    return _get_session(session_id)


@router.post("/{session_id}/complete")
def complete_session(session_id: str):
    """Mark session as paid (called after successful payment)."""
    session = _sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    session.status   = SessionStatus.PAID
    session.end_time = datetime.datetime.utcnow()
    return {"status": "paid", "session_id": session_id}
