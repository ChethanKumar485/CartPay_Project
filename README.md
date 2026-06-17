# 🛒 CartPay — Smart Self-Checkout Trolley System

<div align="center">

![CartPay Logo](docs/images/cartpay-logo.png)

### **Shop. Scan. Pay. Walk Out.**

*A Smart IoT-Based Self-Checkout Shopping Trolley for Modern Supermarkets*

![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Development-blue.svg)
![Platform](https://img.shields.io/badge/Platform-IoT-orange.svg)
![Backend](https://img.shields.io/badge/Backend-FastAPI-success.svg)

</div>

---

## 📖 Overview

CartPay is an IoT-powered smart shopping trolley designed to eliminate long checkout queues in supermarkets and retail stores.

Instead of waiting at billing counters, customers can scan products directly while shopping, verify items using weight sensors, track their bill in real time, pay digitally or via cash kiosks, receive an instant receipt, and exit the store seamlessly through an automated smart gate.

The system combines:

* Barcode Scanning
* Weight-Based Item Verification
* Real-Time Billing
* Digital & Cash Payments
* RFID-Based Smart Exit
* Inventory Integration
* Store Analytics Dashboard

---

## 🎯 Problem Statement

Traditional supermarket checkout systems suffer from:

* Long billing queues
* High staffing requirements
* Manual billing errors
* Barcode switching and item mismatch fraud
* Slow cash transactions
* Poor customer experience during peak hours

CartPay aims to solve these challenges by moving the checkout process directly into the shopping trolley.

---

## ✨ Key Features

### 🛍 Smart Item Scanning

* Barcode-based product identification
* Instant product information retrieval
* Automatic quantity management
* Remove item functionality

### ⚖ Weight-Based Verification

* Load-cell-based basket monitoring
* Scan-to-weight validation
* Mismatch detection alerts
* Theft prevention support

### 📱 Live Billing

* Running total updates in real time
* Itemized cart display
* Quantity and pricing information
* Tax calculations

### ⏳ Expiry Tracking

* Displays product expiry dates
* Near-expiry alerts
* Discount recommendations

### 💳 Multi-Mode Payments

* UPI
* Credit/Debit Cards
* Digital Wallets
* Cash Payment Kiosks

### 🧾 Instant Receipt Generation

* Digital receipt
* SMS receipt
* Email receipt
* Thermal print support

### 🚪 Smart Exit Gate

* RFID verification
* Automated gate opening
* Unpaid session detection

### 🗣 Voice Assistance

* Multi-language support
* Accessibility features
* Audio alerts and announcements

### 📊 Analytics Dashboard

* Live cart tracking
* Revenue analytics
* Product insights
* Theft/mismatch monitoring

---

# 🏗 System Architecture

```text
                    ┌──────────────────────┐
                    │    Cloud Backend     │
                    │ Inventory Database   │
                    │ Payment Services     │
                    │ Analytics Engine     │
                    └──────────┬───────────┘
                               │
                     MQTT / REST APIs
                               │
       ┌───────────────────────┼───────────────────────┐
       │                       │                       │

┌──────▼──────┐      ┌────────▼────────┐     ┌────────▼────────┐
│ Smart Cart  │      │ Customer App    │     │ Admin Dashboard │
└──────┬──────┘      └─────────────────┘     └─────────────────┘
       │
       │
┌──────▼──────┐
│ Cash Kiosk  │
└──────┬──────┘
       │
┌──────▼──────┐
│ Smart Gate  │
└─────────────┘
```

---

# 🛒 Customer Workflow

```text
Pick Cart
    ↓
Scan Product
    ↓
Weight Verification
    ↓
Add To Basket
    ↓
Live Bill Update
    ↓
Checkout
    ↓
Payment
    ↓
Receipt Generated
    ↓
Exit Gate Verification
    ↓
Walk Out
```

---

# ⚙ Hardware Components

| Component                 | Purpose                |
| ------------------------- | ---------------------- |
| ESP32 / Raspberry Pi      | Main Controller        |
| Barcode Scanner           | Product Identification |
| Load Cells + HX711        | Weight Measurement     |
| Touchscreen Display       | User Interface         |
| Speaker Module            | Voice Alerts           |
| RFID Tag                  | Cart Identification    |
| Battery Pack              | Portable Power         |
| Thermal Printer           | Receipt Printing       |
| Cash Validator (Optional) | Cash Transactions      |
| Card Reader (Optional)    | Card Payments          |

---

# 💻 Software Stack

## Embedded System

* ESP-IDF
* Arduino Framework
* Python (Raspberry Pi)

## Backend

* FastAPI
* Node.js (Alternative)

## Database

* PostgreSQL
* Redis
* MongoDB (Optional)

## Mobile App

* Flutter
* React Native

## Dashboard

* React.js
* Chart.js
* Recharts

## Communication

* MQTT
* REST APIs
* WebSockets

## Cloud

* AWS
* Firebase

---

# 🗄 Database Design

## Items

| Field            | Type    |
| ---------------- | ------- |
| item_id          | UUID    |
| barcode          | String  |
| name             | String  |
| price            | Decimal |
| reference_weight | Float   |
| expiry_date      | Date    |

## Sessions

| Field      | Type      |
| ---------- | --------- |
| session_id | UUID      |
| cart_id    | UUID      |
| user_id    | UUID      |
| status     | String    |
| start_time | Timestamp |

## Transactions

| Field          | Type    |
| -------------- | ------- |
| transaction_id | UUID    |
| session_id     | UUID    |
| amount         | Decimal |
| payment_mode   | String  |
| status         | String  |

---

# 🔌 API Endpoints

| Method | Endpoint                     |
| ------ | ---------------------------- |
| POST   | /session/start               |
| POST   | /session/{id}/scan           |
| DELETE | /session/{id}/item/{item_id} |
| GET    | /session/{id}/total          |
| POST   | /session/{id}/verify-weight  |
| POST   | /session/{id}/pay/digital    |
| POST   | /session/{id}/complete       |
| GET    | /items/{barcode}             |
| GET    | /alerts                      |
| GET    | /analytics/dashboard         |

---

# 🔒 Security Features

* TLS encrypted communication
* Device authentication tokens
* Secure payment gateway integration
* Role-based access control
* Tamper detection alerts
* Secure RFID validation

---

# 💰 Estimated Prototype Cost

| Component            | Cost (₹)    |
| -------------------- | ----------- |
| ESP32 / Raspberry Pi | 500 – 3500  |
| Barcode Scanner      | 1500 – 3000 |
| Load Cells + HX711   | 600 – 1000  |
| Touchscreen          | 2500 – 4500 |
| Battery System       | 800 – 1500  |
| RFID Components      | 200 – 500   |
| Misc Electronics     | 1000 – 2000 |

### Estimated Total

**₹7,400 – ₹16,600 per trolley**

---

# 🚀 Development Roadmap

## Phase 1 — MVP

* Barcode scanning
* Weight verification
* Local backend
* Bill generation

## Phase 2 — Pilot Deployment

* Multiple carts
* RFID exit gate
* UPI integration
* Cash kiosk support

## Phase 3 — Production Scale

* AI-powered item recognition
* ERP integration
* Advanced analytics
* Fleet management

## Phase 4 — Future Vision

* Grab-and-Go Shopping
* Computer Vision Checkout
* Personalized Offers
* Smart Shelf Integration
* Indoor Navigation
* Autonomous Cart Assistance

---

# 📸 Project Screenshots

## Smart Trolley

```text
 _______________________
|   CARTPAY DISPLAY     |
|  Total: ₹1250         |
|_______________________|

       Basket
   ________________
  |                |
  | Shopping Cart  |
  |________________|

      O        O
```

---

## Checkout Screen

```text
---------------------------------
 CARTPAY

 Milk 1L
 ₹65 × 2

 Total ₹130

 Cart Total ₹1250

 [Checkout]
---------------------------------
```

---

# 📁 Project Structure

```text
CartPay/
│
├── firmware/
│   ├── esp32/
│   └── raspberry_pi/
│
├── backend/
│   ├── api/
│   ├── database/
│   └── mqtt/
│
├── mobile-app/
│
├── dashboard/
│
├── docs/
│   ├── diagrams/
│   ├── images/
│   └── presentations/
│
├── hardware/
│
└── README.md
```

---

# 🤝 Contributing

Contributions are welcome.

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to GitHub
5. Submit a Pull Request

---

# 📜 License

This project is licensed under the MIT License.

See the LICENSE file for details.

---

# 👨‍💻 Author

**Chethan Kumar**

CartPay — Smart Self-Checkout Trolley System

*"Transforming Retail Through Smart Checkout Technology."*

---

## ⭐ Support

If you found this project useful:

⭐ Star the repository

🍴 Fork the project

📢 Share it with others

💡 Contribute new ideas and features

---

<div align="center">

### 🛒 CartPay

### Shop. Scan. Pay. Walk Out.

</div>
