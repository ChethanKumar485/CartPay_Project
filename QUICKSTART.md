# CartPay — Smart Self-Checkout Trolley System
### Complete Project Package

---

## What's inside

```
CartPay_Project/
├── prototype/              ← Interactive UI demo (open index.html in browser — no server needed)
│   └── index.html
├── backend/                ← Python FastAPI server
│   ├── app/
│   │   ├── main.py
│   │   ├── api/            ← sessions, items, payments, alerts, analytics
│   │   ├── models/         ← Pydantic schemas
│   │   └── services/       ← inventory, weight logic
│   ├── tests/              ← pytest unit tests
│   ├── requirements.txt
│   └── Dockerfile
├── firmware/
│   └── cartpay_cart.ino    ← ESP32 Arduino firmware for the smart cart
├── admin-dashboard/
│   └── index.html          ← Staff live monitoring dashboard (no server needed)
├── docker-compose.yml      ← One-command full-stack deployment
├── mosquitto.conf          ← MQTT broker config
└── README.md               ← Full project blueprint (architecture, BOM, roadmap)
```

---

## Quick start

### 1. Interactive prototype (no install required)
Open `prototype/index.html` in any modern browser.
Tap items to scan them. Use the demo controls to simulate mismatches.
Click Checkout to walk through the full payment + exit gate flow.

### 2. Run the backend locally
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
# API docs: http://localhost:8000/docs
```

### 3. Run tests
```bash
cd backend
pytest tests/ -v
```

### 4. Full stack with Docker
```bash
docker-compose up --build
# API:       http://localhost:8000/docs
# Dashboard: http://localhost:3000
```

### 5. Flash the cart firmware
1. Install Arduino IDE 2.x and add the ESP32 board package (Espressif).
2. Install libraries listed at the top of `firmware/cartpay_cart.ino`.
3. Edit WiFi credentials and API base URL in the config section.
4. Select board "ESP32 Dev Module", flash.

---

## Key API endpoints

| Method | URL | Purpose |
|---|---|---|
| POST | `/session/start?cart_id=X` | Start shopping session |
| POST | `/session/{id}/scan` | Scan a barcode + measured weight |
| DELETE | `/session/{id}/item` | Remove scanned item |
| GET | `/session/{id}/total` | Current bill |
| POST | `/pay/{id}/digital` | Digital payment |
| POST | `/pay/kiosk/{rfid}/cash/pay` | Cash payment with change calc |
| GET | `/pay/gate/{rfid}/check` | Exit gate verification |
| GET | `/items/{barcode}` | Item lookup |
| GET | `/analytics/dashboard` | Store stats |

Full interactive docs: `http://localhost:8000/docs`

---

*CartPay v1.0 · Built as an engineering capstone project.*
