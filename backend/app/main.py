"""
CartPay Backend — FastAPI Entry Point
=====================================
Run locally:
    uvicorn app.main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import sessions, items, payments, alerts, analytics

app = FastAPI(
    title="CartPay API",
    description="Smart self-checkout trolley system backend",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sessions.router,   prefix="/session",   tags=["Sessions"])
app.include_router(items.router,      prefix="/items",     tags=["Items"])
app.include_router(payments.router,   prefix="/pay",       tags=["Payments"])
app.include_router(alerts.router,     prefix="/alerts",    tags=["Alerts"])
app.include_router(analytics.router,  prefix="/analytics", tags=["Analytics"])


@app.get("/health")
def health():
    return {"status": "ok", "service": "CartPay API"}
