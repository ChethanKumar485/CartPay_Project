"""CartPay — Alerts Router"""
from fastapi import APIRouter
from app.models.schemas import Alert, AlertType
import uuid, datetime

router = APIRouter()
_alerts: list[Alert] = []


@router.get("/", response_model=list[Alert])
def get_alerts(resolved: bool = False):
    return [a for a in _alerts if a.resolved == resolved]


@router.post("/", response_model=Alert, status_code=201)
def create_alert(session_id: str, cart_id: str, alert_type: AlertType, detail: str):
    a = Alert(
        alert_id   = f"ALT-{uuid.uuid4().hex[:6].upper()}",
        session_id = session_id,
        cart_id    = cart_id,
        alert_type = alert_type,
        detail     = detail,
    )
    _alerts.append(a)
    return a


@router.patch("/{alert_id}/resolve")
def resolve_alert(alert_id: str):
    for a in _alerts:
        if a.alert_id == alert_id:
            a.resolved = True
            return {"resolved": True}
    return {"resolved": False}
