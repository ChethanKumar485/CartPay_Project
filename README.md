# CartPay — Smart Self-Checkout Trolley System

> **Tagline:** *Shop. Scan. Pay. Walk Out.*
> Alternate name options (all starting with "CP"): **CPilot**, **CartPulse**, **CPCart**, **CartProof**, **CPSmart**

---

## 1. Executive Summary

CartPay is a smart shopping trolley system designed to eliminate billing-counter queues in supermarkets (such as DMart, BigBazaar, Reliance Smart, etc.). Each trolley is fitted with a barcode scanner, a weight sensor, a touchscreen display, and a payment module. As a customer shops, they scan each item, the cart verifies that the correct item was placed inside using weight matching, and the running total is shown live. At the end of the shopping trip, the customer pays directly from the cart (digital or cash), receives a bill instantly, gets a carry bag recommendation based on the total weight of items, and walks straight out through a smart exit gate — no separate billing queue required.

---

## 2. Problem Statement

In most supermarkets today:

- Customers spend a large portion of their visit waiting in billing queues, especially during peak hours and festive seasons.
- Manual billing is slow, error-prone, and requires significant staffing.
- Item mismatches (wrong item billed, missed items, switched barcodes) cause both customer disputes and store losses.
- Carry bags are often given in incorrect sizes, leading to wastage or insufficient packing.
- Cash handling at counters is slow due to manual change calculation and counting errors.

---

## 3. Proposed Solution

A network of **smart trolleys**, each acting as a mobile self-checkout point, connected to the supermarket's central inventory and billing server over Wi-Fi/MQTT. The trolley:

1. Scans items as they are picked up.
2. Verifies the item physically placed in the cart matches the scanned barcode using a weight-sensing system.
3. Displays item details (name, price, expiry, quantity) and a live running total.
4. Lets the customer pay by digital wallet/UPI/card **or** cash, with automatic change calculation.
5. Recommends and dispenses the correct carry bag size based on total cart weight.
6. Generates a digital/printed bill instantly.
7. Syncs the "paid" status with a smart exit gate so the customer can walk out without further checks.

---

## 4. Core Features

### 4.1 Barcode Scanning & Item Recognition
- Onboard laser/camera-based barcode scanner mounted on the cart handle.
- On scan, fetches item name, price, weight, category, and expiry date from the central inventory database.
- Supports re-scanning to increase quantity, and a "remove item" function if the customer changes their mind.

### 4.2 Real-Time Display & Running Bill
- 7"–10" touchscreen on the cart shows: item name, unit price, quantity, expiry date (with near-expiry warnings), and running total.
- Color-coded alerts for items nearing expiry (e.g., yellow if expiring within 3 days, red if expired).

### 4.3 Weight-Based Item Verification (Anti-Mismatch System)
- Load cells under the cart's basket continuously measure total weight.
- Each item in the database has a stored reference weight and an acceptable tolerance range.
- After each scan, the system expects the cart's weight to increase by approximately the scanned item's weight (within tolerance).
- If the actual weight change doesn't match (e.g., a cheaper item is scanned but a costlier item is placed), the system flags a **mismatch alert** — on-screen warning, audio cue, and optional notification to nearby staff.

### 4.4 Expiry Date Tracking & Alerts
- Every scanned item's expiry date is displayed.
- Items close to expiry can trigger a "discounted item" suggestion pop-up, encouraging faster turnover of near-expiry stock (useful for the store too).

### 4.5 Multi-Mode Payment
- **Digital payments**: UPI, debit/credit card (via a card reader on the cart), and wallet integration through a linked mobile app.
- **Cash payments**: Either via an onboard note/coin acceptor on premium carts, or via dedicated **Cash Payment Kiosks** near the exit (recommended for cost efficiency — see Section 11).
- **Automatic amount verification**: The system totals the cash inserted, compares it with the bill amount, and:
  - If cash given ≥ bill → calculates and dispenses/displays the correct change.
  - If cash given < bill → displays the remaining balance due and prompts for more cash or a digital top-up.

### 4.6 Auto Carry Bag Recommendation
- Based on the cumulative weight of all scanned items, the system suggests a bag size (small/medium/large/jumbo) and can trigger an automatic bag dispenser at the exit kiosk.

### 4.7 Instant Bill Generation
- A digital bill (sent to the customer's app/email/SMS) and an optional printed receipt (via a compact thermal printer) are generated the moment payment is confirmed.

### 4.8 Smart Exit Gate Integration
- Each cart carries an RFID/NFC tag. On payment completion, the cart's session is marked "paid" on the server.
- The exit gate reads the cart's tag; if "paid" = true, the gate opens automatically. If not, an alarm/staff alert is triggered.

### 4.9 Accessibility & Voice Assistance
- Text-to-speech announcements for item name, price, and total — useful for visually impaired shoppers and general convenience.
- Multi-language support (e.g., English, Hindi, Kannada, Tamil) based on customer profile or manual selection.

### 4.10 Store Analytics Dashboard
- Real-time dashboard for store managers: live cart locations/status, most-scanned items, mismatch/theft alerts, average checkout time, near-expiry inventory reports.

---

## 5. System Architecture

```
                ┌────────────────────────────┐
                │        Cloud Backend        │
                │  (Inventory DB, Sessions,   │
                │   Payments, Analytics API)  │
                └──────────────┬───────────────┘
                                │ MQTT / REST / WebSocket
        ┌───────────────────────┼───────────────────────┐
        │                        │                        │
┌───────▼────────┐      ┌────────▼────────┐     ┌────────▼────────┐
│  Smart Trolley  │      │  Customer App    │     │ Admin Dashboard │
│  (ESP32 / RPi)  │      │ (Flutter/React   │     │   (React Web)   │
│  - Barcode Scan │      │  Native)         │     │  - Live carts   │
│  - Load Cell    │      │ - Account/Wallet │     │  - Alerts       │
│  - Touchscreen  │      │ - Digital Bill   │     │  - Inventory    │
│  - Speaker      │      └──────────────────┘     │  - Reports      │
│  - RFID Tag     │                                └─────────────────┘
└────────┬────────┘
         │
┌────────▼────────┐     ┌─────────────────────┐
│ Cash Kiosk /     │     │  Smart Exit Gate     │
│ Note+Coin Module │     │  (RFID reader +      │
│ (optional)       │     │   gate controller)   │
└──────────────────┘     └─────────────────────┘
```

---

## 6. Hardware Components (Bill of Materials)

| Component | Purpose | Example / Notes |
|---|---|---|
| ESP32 / Raspberry Pi 4 | Main controller for cart | ESP32 for low-cost MVP, RPi4 if camera-based verification is added |
| Barcode scanner module | Item identification | UART laser scanner (e.g., Honeywell 1900) or camera + OpenCV/pyzbar |
| Load cells (x4) + HX711 amplifier | Weight measurement of basket | One under each corner of the basket tray |
| 7"–10" capacitive touchscreen | Display item info & running bill | HDMI/SPI display |
| Speaker module | Voice/audio alerts | I2S small speaker |
| RFID/NFC tag + reader | Cart identity & exit gate verification | Passive RFID tag on cart, reader at gate |
| Rechargeable battery + charging dock | Power supply | Li-ion pack with docking station at cart bay |
| Card reader (optional) | Digital card payments | Standard POS card reader module |
| Note/coin acceptor (optional, per-cart or kiosk) | Cash payments | JCM/ICT bill validator + coin hopper |
| Thermal printer (optional) | Printed receipts | 58mm thermal printer |
| Cart frame/housing | Mounting all components | Custom-fabricated enclosure |

---

## 7. Software Modules

1. **Embedded Cart Firmware** — runs on ESP32/RPi, handles scanning, weight sampling, display rendering, and communication with the backend.
2. **Backend Server** — REST + WebSocket/MQTT API, manages inventory, sessions, transactions, and alerts.
3. **Customer Mobile App** — account management, digital wallet, live bill view, e-receipts, loyalty points.
4. **Admin/Staff Dashboard** — live monitoring of carts, mismatch alerts, inventory and analytics.
5. **Payment Module** — integrates UPI/card gateways and handles cash-validation logic.
6. **Exit Gate Controller** — verifies "paid" status via RFID before opening the gate.

---

## 8. Customer Journey (Step-by-Step Workflow)

1. Customer picks a CartPay trolley, taps in via RFID card / app QR code (optional login for loyalty benefits).
2. Customer picks an item, scans its barcode using the cart-mounted scanner.
3. The cart display shows item name, price, expiry date, and updates the running total.
4. Customer places the item in the basket. The weight sensor confirms the item matches the scanned barcode (within tolerance).
   - If mismatch detected → on-screen + audio alert asks the customer to re-check the item.
5. Steps 2–4 repeat for every item. Customer can remove/undo a scanned item if needed (weight and bill auto-adjust).
6. When done shopping, customer taps "Checkout" on the cart screen.
7. Final bill is displayed with itemized list, total amount, and a recommended carry bag size.
8. Customer pays:
   - **Digitally** (UPI/card/wallet) directly from the cart or linked app, **or**
   - **In cash** at a nearby Cash Kiosk, where the system verifies the amount and dispenses change if needed.
9. On successful payment, a digital/printed bill is generated and the cart's RFID tag is marked "paid" on the server.
10. Customer picks up the recommended bag (auto-dispensed at the bagging counter) and walks through the smart exit gate, which opens automatically after verifying the "paid" status.

---

## 9. Anti-Mismatch / Anti-Theft Logic

**Goal:** Ensure the item physically placed in the cart matches what was scanned, without requiring per-item perfect precision.

**Approach:**

- Each item record stores a `reference_weight` and a `tolerance_percent` (e.g., ±5% for packaged goods, wider for loose produce).
- After each scan, the system calculates `expected_total_weight = sum(reference_weight × quantity)` for all scanned items.
- The load cells report `actual_total_weight` after each placement.
- The system checks: `|actual_total_weight − expected_total_weight| ≤ tolerance_band`, where `tolerance_band` is a cumulative percentage of the expected total (e.g., ±3% of running total weight), to avoid small sensor-noise false alarms.
- If the difference exceeds the tolerance band:
  - Cart screen shows: *"Please verify the last item placed — weight mismatch detected."*
  - Audio cue plays.
  - If unresolved after a short timer, an alert is sent to the staff dashboard with the cart ID and last-scanned item.
- **Optional upgrade (Phase 3):** Add a small camera above the basket with a lightweight image-recognition model to visually cross-check the item against the scanned barcode for higher accuracy.

---

## 10. Cash Payment & Auto Change Calculation

**Design choice:** Rather than putting an expensive note/coin acceptor on *every* cart (costly and bulky), CartPay uses a small number of **Cash Payment Kiosks** near the exit. The customer's cart session (and bill) is retrieved by scanning the cart's RFID tag or a QR code shown on the cart screen.

**Logic:**

1. Kiosk fetches the pending bill amount for the scanned cart session.
2. Customer inserts notes/coins.
3. The validator reports the total amount inserted in real time.
4. System compares `amount_inserted` vs `bill_amount`:
   - If `amount_inserted < bill_amount` → display `"Amount due: ₹X"` and continue accepting cash.
   - If `amount_inserted == bill_amount` → mark transaction complete.
   - If `amount_inserted > bill_amount` → calculate `change = amount_inserted − bill_amount`, dispense via coin/note hopper (or, for simplicity in early phases, direct the customer to a staff member with a printed change voucher).
5. On completion, the session is marked "paid," and the receipt is printed/sent digitally.

> Premium carts in later phases can optionally include a compact onboard note acceptor for customers who prefer not to walk to a kiosk.

---

## 11. Carry Bag Recommendation Logic

| Total Cart Weight | Recommended Bag Size |
|---|---|
| Up to 2 kg | Small bag |
| 2 kg – 5 kg | Medium bag |
| 5 kg – 10 kg | Large bag |
| Above 10 kg | Jumbo bag / multiple bags |

- The recommendation is shown on the checkout screen.
- At the exit, an automated bag dispenser (simple coin/lever mechanism) releases the suggested bag size when the customer confirms.

---

## 12. Database Schema (Core Tables)

- **Items**: `item_id`, `barcode`, `name`, `category`, `price`, `reference_weight`, `tolerance_percent`, `expiry_date`, `image_url`
- **Carts**: `cart_id`, `rfid_tag`, `status` (idle/in-use/charging), `battery_level`
- **Sessions**: `session_id`, `cart_id`, `user_id` (nullable), `start_time`, `end_time`, `status` (active/paid/abandoned)
- **SessionItems**: `session_id`, `item_id`, `quantity`, `scanned_weight_contribution`
- **Transactions**: `transaction_id`, `session_id`, `amount`, `payment_mode` (digital/cash), `change_given`, `status`, `timestamp`
- **Users**: `user_id`, `name`, `phone`, `loyalty_points`, `preferred_language`
- **Bags**: `bag_size`, `weight_min`, `weight_max`
- **Alerts**: `alert_id`, `session_id`, `cart_id`, `alert_type` (mismatch/theft/low_battery), `timestamp`, `resolved`

---

## 13. Sample API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/session/start` | Start a new cart session (assigns cart to user) |
| POST | `/session/{id}/scan` | Register a scanned item, update bill |
| DELETE | `/session/{id}/item/{item_id}` | Remove a scanned item |
| GET | `/session/{id}/total` | Get current running total and item list |
| POST | `/session/{id}/verify-weight` | Submit current load cell reading for mismatch check |
| POST | `/session/{id}/pay/digital` | Process digital payment |
| POST | `/kiosk/{cart_rfid}/pay/cash` | Cash payment processing at kiosk |
| POST | `/session/{id}/complete` | Mark session as paid, generate bill |
| GET | `/items/{barcode}` | Fetch item details by barcode |
| GET | `/alerts` | Fetch active alerts for staff dashboard |
| GET | `/analytics/dashboard` | Aggregated store analytics |

---

## 14. Technology Stack

- **Embedded firmware**: C/C++ (Arduino framework or ESP-IDF) on ESP32, or Python on Raspberry Pi for camera-based features.
- **Weight sensing**: HX711 load cell amplifier with calibration routines.
- **Backend**: Python (FastAPI) or Node.js (Express), exposing REST + WebSocket APIs.
- **Database**: PostgreSQL for transactional data (sessions, transactions), Redis for fast session/state caching, optional MongoDB for the product catalog.
- **Real-time communication**: MQTT broker (e.g., EMQX/Mosquitto) for cart-to-server messaging; WebSockets for live dashboard/app updates.
- **Customer App**: Flutter or React Native (cross-platform).
- **Admin Dashboard**: React + a charting library (e.g., Chart.js/Recharts).
- **Payments**: Razorpay/UPI APIs for digital payments; serial/RS232 interface for cash validator hardware.
- **Cloud hosting**: AWS (EC2 + RDS + IoT Core) or Firebase for a lighter-weight pilot deployment.

---

## 15. Security & Privacy Considerations

- All cart-to-server communication encrypted via TLS.
- Each cart authenticates with the backend using a unique device token (rotated periodically).
- Payment data handled through certified payment gateways only — CartPay never stores raw card numbers.
- Customer personal data (phone numbers, purchase history) stored with access controls and anonymized for analytics where possible.
- Tamper-detection sensors on the cart housing to flag attempts to disable the load cells or scanner.
- Exit gate logic always defaults to "alert staff" on any communication failure, rather than silently allowing exit — avoiding false negatives in theft detection.

---

## 16. Implementation Roadmap

### Phase 1 — Prototype (College Project / MVP)
- Single cart built with ESP32, barcode scanner, load cells, and a small touchscreen.
- Local backend (FastAPI) running on a laptop, simple SQLite/PostgreSQL database.
- Core features: scan → display → weight check → digital bill generation (no real payment gateway, simulate with test transactions).

### Phase 2 — Pilot Deployment
- 5–10 carts deployed in a small store section.
- Real payment gateway integration (UPI sandbox → production).
- Cash kiosk near exit, RFID-based exit gate.
- Admin dashboard for staff with live alerts.

### Phase 3 — Full Rollout
- Fleet management for large numbers of carts (battery monitoring, auto-charging docks).
- Camera-based item verification as a secondary anti-theft layer.
- Integration with the store's existing POS/ERP and loyalty systems.
- Advanced analytics: demand forecasting, near-expiry markdown suggestions, personalized offers.

---

## 17. Estimated Cost (Per Cart, Prototype Stage — Approximate, INR)

| Component | Approx. Cost (₹) |
|---|---|
| ESP32 / Raspberry Pi | 500 – 3,500 |
| Barcode scanner module | 1,500 – 3,000 |
| Load cells + HX711 (x4) | 600 – 1,000 |
| 7" touchscreen display | 2,500 – 4,500 |
| Speaker + misc. electronics | 300 – 600 |
| RFID tag + reader (shared cost) | 200 – 500 per cart |
| Battery + charging components | 800 – 1,500 |
| Frame/housing/wiring | 1,000 – 2,000 |
| **Estimated total per cart** | **≈ ₹7,400 – ₹16,600** |

*(Cash kiosks, exit gates, and servers are shared infrastructure costs, not per-cart.)*

---

## 18. Challenges & Mitigations

| Challenge | Mitigation |
|---|---|
| Weight tolerance for loose/variable-weight items (fruits, vegetables) | Use a wider tolerance band or a separate "weigh-and-scan" station for produce |
| Customers placing items back on shelves after scanning | "Remove item" workflow with weight re-verification |
| Network connectivity in large stores | Local edge processing on cart + periodic sync; offline queueing of transactions |
| Battery life of carts | Swappable battery packs + auto-docking charging stations |
| Customer trust in automated billing | Random spot-checks by staff initially; transparent itemized digital receipts |
| Cash handling accuracy | Centralized, well-maintained note/coin validators at kiosks rather than per-cart |

---

## 19. Future Enhancements

- Computer-vision-based "grab and go" checkout (no scanning required) as a long-term goal.
- AI-driven personalized recommendations and recipe suggestions based on cart contents.
- Dynamic discount alerts for near-expiry items, reducing store wastage.
- Integration with home delivery — customers can convert an in-store cart session into a home delivery order.
- Loyalty and rewards system tied to the customer app.

---

## 20. Conclusion

CartPay reimagines the supermarket checkout experience by moving billing, item verification, payment, and bagging directly into the shopping cart itself. By combining low-cost IoT hardware (barcode scanning + weight sensing) with a robust backend and clear anti-mismatch logic, it directly addresses the long-queue problem common in supermarkets, while also giving store owners better inventory visibility, reduced losses from mismatches/theft, and richer analytics. The phased roadmap makes it practical to start as a single-cart college prototype and scale up to a full store deployment over time.
still more implementation will be done,in further days.

---

## 🤝 Contributing

Contributions are welcome! To contribute:
Contributions are welcome! Feel free to fork this repository and submit pull requests.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

Copyright © 2026 Chethan Kumar

---
