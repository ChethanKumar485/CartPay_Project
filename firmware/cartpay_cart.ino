/**
 * CartPay — Smart Cart Firmware
 * ==============================
 * Target board : ESP32 (38-pin DevKit or WROOM-32)
 * Arduino IDE  : 2.x  |  Board package: esp32 by Espressif ≥ 3.0
 *
 * Hardware wiring:
 *   Barcode scanner (UART)   → GPIO 16 (RX2), GPIO 17 (TX2)
 *   HX711 DOUT               → GPIO 4
 *   HX711 SCK                → GPIO 5
 *   TFT Display (SPI)        → standard SPI + GPIO 15 CS, GPIO 2 DC, GPIO 0 RST
 *   Buzzer (active, 5V)      → GPIO 18 (via NPN transistor)
 *   RFID RC522 (SPI)         → GPIO 21 SS, GPIO 22 RST
 *   RGB status LED           → GPIO 25 R, GPIO 26 G, GPIO 27 B
 *
 * Libraries required (install via Library Manager):
 *   - HX711 by bogde
 *   - TFT_eSPI by Bodmer (configure User_Setup.h for your display)
 *   - MFRC522 by GithubCommunity
 *   - ArduinoJson by Benoit Blanchon
 *   - PubSubClient by Nick O'Leary  (MQTT)
 *   - WiFi (built-in ESP32)
 *   - HTTPClient (built-in ESP32)
 */

#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <HX711.h>
#include <TFT_eSPI.h>
#include <MFRC522.h>
#include <PubSubClient.h>

// ─── Configuration ────────────────────────────────────────────────────────────
#define WIFI_SSID       "YOUR_WIFI_SSID"
#define WIFI_PASS       "YOUR_WIFI_PASSWORD"
#define API_BASE        "http://192.168.1.100:8000"   // CartPay backend IP
#define MQTT_BROKER     "192.168.1.100"
#define MQTT_PORT       1883
#define CART_ID         "CART-001"
#define RFID_TAG        "RFID-ABC123"

// ─── Pin definitions ─────────────────────────────────────────────────────────
#define HX711_DOUT  4
#define HX711_SCK   5
#define BUZZER_PIN  18
#define LED_R       25
#define LED_G       26
#define LED_B       27
#define RFID_SS     21
#define RFID_RST    22

// ─── Globals ─────────────────────────────────────────────────────────────────
HX711       scale;
TFT_eSPI    tft;
MFRC522     rfid(RFID_SS, RFID_RST);
WiFiClient  wifiClient;
PubSubClient mqtt(wifiClient);

HardwareSerial scannerSerial(2);   // UART2 for barcode scanner

String  sessionId       = "";
float   subtotal        = 0.0;
int     itemCount       = 0;
float   totalWeightG    = 0.0;
float   scaleOffset     = 0.0;
bool    mismatchActive  = false;

// ─── Helpers ─────────────────────────────────────────────────────────────────

void setLED(bool r, bool g, bool b) {
  digitalWrite(LED_R, r ? HIGH : LOW);
  digitalWrite(LED_G, g ? HIGH : LOW);
  digitalWrite(LED_B, b ? HIGH : LOW);
}

void beep(int ms = 80) {
  digitalWrite(BUZZER_PIN, HIGH);
  delay(ms);
  digitalWrite(BUZZER_PIN, LOW);
}

void alertBeep() {
  for (int i = 0; i < 3; i++) { beep(120); delay(80); }
}

// ─── Display ─────────────────────────────────────────────────────────────────

void drawHeader() {
  tft.fillRect(0, 0, tft.width(), 28, TFT_DARKGREEN);
  tft.setTextColor(TFT_WHITE, TFT_DARKGREEN);
  tft.setTextSize(1);
  tft.setCursor(6, 9);
  tft.print("CARTPAY  |  " + String(CART_ID));
}

void drawTotals() {
  tft.fillRect(0, 28, tft.width(), tft.height() - 28, TFT_BLACK);
  tft.setTextColor(TFT_WHITE, TFT_BLACK);
  tft.setTextSize(1);

  tft.setCursor(6, 38);
  tft.print("Items : " + String(itemCount));

  tft.setCursor(6, 56);
  tft.print("Weight: " + String(totalWeightG, 0) + " g");

  tft.setTextSize(2);
  tft.setCursor(6, 80);
  tft.setTextColor(TFT_GREEN, TFT_BLACK);
  tft.print("Total: Rs " + String(subtotal, 2));

  if (mismatchActive) {
    tft.setTextSize(1);
    tft.setTextColor(TFT_RED, TFT_BLACK);
    tft.setCursor(6, 112);
    tft.print("! MISMATCH — check last item");
  }
}

void showScanFeedback(String name, float price) {
  tft.fillRect(0, 130, tft.width(), 60, TFT_NAVY);
  tft.setTextColor(TFT_CYAN, TFT_NAVY);
  tft.setTextSize(1);
  tft.setCursor(6, 138);
  tft.print(name.substring(0, 28));
  tft.setCursor(6, 154);
  tft.print("Rs " + String(price, 2) + "  added");
}

void showReady() {
  tft.fillRect(0, 130, tft.width(), 60, TFT_BLACK);
  tft.setTextColor(TFT_DARKGREY, TFT_BLACK);
  tft.setTextSize(1);
  tft.setCursor(6, 154);
  tft.print("Scan next item...");
}

// ─── WiFi & MQTT ─────────────────────────────────────────────────────────────

void connectWiFi() {
  Serial.print("[WiFi] Connecting");
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) { delay(400); Serial.print("."); }
  Serial.println(" connected: " + WiFi.localIP().toString());
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
  // Handle server→cart messages (e.g., "session/paid", "alert/mismatch")
  String msg = "";
  for (unsigned int i = 0; i < length; i++) msg += (char)payload[i];
  Serial.println("[MQTT] " + String(topic) + " → " + msg);
  if (msg == "PAID") { setLED(false, true, false); beep(200); delay(200); beep(200); }
}

void connectMQTT() {
  mqtt.setServer(MQTT_BROKER, MQTT_PORT);
  mqtt.setCallback(mqttCallback);
  while (!mqtt.connected()) {
    if (mqtt.connect(CART_ID)) {
      mqtt.subscribe(("cartpay/cart/" + String(CART_ID) + "/cmd").c_str());
      Serial.println("[MQTT] Connected");
    } else {
      delay(2000);
    }
  }
}

// ─── API Calls ────────────────────────────────────────────────────────────────

String startSession() {
  HTTPClient http;
  http.begin(String(API_BASE) + "/session/start?cart_id=" + CART_ID);
  int code = http.POST("");
  if (code == 201) {
    DynamicJsonDocument doc(512);
    deserializeJson(doc, http.getString());
    http.end();
    return doc["session_id"].as<String>();
  }
  http.end();
  return "";
}

bool scanItemAPI(String barcode, float measuredWeight,
                 String &outName, float &outPrice) {
  if (sessionId == "") return false;

  HTTPClient http;
  http.begin(String(API_BASE) + "/session/" + sessionId + "/scan");
  http.addHeader("Content-Type", "application/json");

  DynamicJsonDocument req(256);
  req["barcode"]         = barcode;
  req["measured_weight"] = measuredWeight;

  String body; serializeJson(req, body);
  int code = http.POST(body);
  bool ok = false;

  if (code == 200) {
    DynamicJsonDocument res(2048);
    deserializeJson(res, http.getString());
    subtotal       = res["subtotal"];
    itemCount      = res["scan_events"].size();
    totalWeightG   = res["total_weight"];
    mismatchActive = res["mismatch_flag"];

    // Find last scanned item name for display
    for (JsonObject item : res["items"].as<JsonArray>()) {
      if (item["barcode"].as<String>() == barcode) {
        outName  = item["item_name"].as<String>();
        outPrice = item["unit_price"];
      }
    }
    ok = true;
  }
  http.end();
  return ok;
}

void publishAlert(String alertType, String detail) {
  DynamicJsonDocument doc(256);
  doc["cart_id"]    = CART_ID;
  doc["alert_type"] = alertType;
  doc["detail"]     = detail;
  String msg; serializeJson(doc, msg);
  mqtt.publish("cartpay/alerts", msg.c_str());
}

// ─── Scale ───────────────────────────────────────────────────────────────────

void calibrateScale() {
  scale.begin(HX711_DOUT, HX711_SCK);
  scale.set_scale(2280.f);   // adjust with known calibration weight
  scale.tare();
  scaleOffset = 0;
  Serial.println("[Scale] Tared and ready");
}

float readWeightG() {
  if (scale.is_ready()) {
    return max(0.0f, scale.get_units(5));
  }
  return 0.0f;
}

// ─── Barcode scanner ──────────────────────────────────────────────────────────

String readBarcode() {
  String barcode = "";
  unsigned long start = millis();
  while (millis() - start < 200) {         // 200 ms window
    while (scannerSerial.available()) {
      char c = (char)scannerSerial.read();
      if (c == '\r' || c == '\n') { if (barcode.length() > 5) return barcode; }
      else barcode += c;
    }
  }
  return "";
}

// ─── Setup ───────────────────────────────────────────────────────────────────

void setup() {
  Serial.begin(115200);
  scannerSerial.begin(9600, SERIAL_8N1, 16, 17);

  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LED_R, OUTPUT); pinMode(LED_G, OUTPUT); pinMode(LED_B, OUTPUT);

  tft.init();
  tft.setRotation(1);
  tft.fillScreen(TFT_BLACK);
  drawHeader();

  SPI.begin();
  rfid.PCD_Init();

  calibrateScale();
  connectWiFi();
  connectMQTT();

  sessionId = startSession();
  Serial.println("[Session] " + sessionId);

  setLED(false, false, true);   // blue = session active
  showReady();
  drawTotals();
}

// ─── Main loop ────────────────────────────────────────────────────────────────

float weightBefore = 0.0;

void loop() {
  if (!mqtt.connected()) connectMQTT();
  mqtt.loop();

  String barcode = readBarcode();

  if (barcode.length() > 0) {
    beep(60);
    setLED(false, false, true);

    weightBefore = readWeightG();

    // Small delay to let the item settle on the scale
    delay(600);
    float weightAfter  = readWeightG();
    float itemDelta    = weightAfter - weightBefore;

    String itemName = "Unknown";
    float  itemPrice = 0;

    bool apiOk = scanItemAPI(barcode, itemDelta, itemName, itemPrice);

    if (!apiOk) {
      tft.fillRect(0, 130, tft.width(), 60, TFT_RED);
      tft.setTextColor(TFT_WHITE, TFT_RED);
      tft.setCursor(6, 150);
      tft.print("Item not found!");
      alertBeep();
      setLED(true, false, false);
      delay(2000);
    } else if (mismatchActive) {
      alertBeep();
      setLED(true, false, false);
      publishAlert("mismatch", "Weight mismatch on barcode " + barcode);
    } else {
      beep(80);
      setLED(false, true, false);
    }

    drawTotals();
    showScanFeedback(itemName, itemPrice);
    delay(2000);
    showReady();
    if (!mismatchActive) setLED(false, false, true);
  }

  delay(50);
}
