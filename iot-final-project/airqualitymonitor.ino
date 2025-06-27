#include <WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// WiFi and MQTT details
const char* ssid = "iPhone 13 Pro";
const char* password = "11223344";
const char* mqtt_server = "172.20.10.8";
const int mqtt_port = 1883;
const char* topic = "esp32/air_quality";

// OLED config
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

// Pins
#define MQ2_PIN 7
#define MQ135_PIN 8
#define GREEN_LED 5
#define BLUE_LED 21
#define RED_LED 6
#define BUZZER_PIN 4

WiFiClient espClient;
PubSubClient client(espClient);

void setup_wifi() {
  Serial.print("Connecting to WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected. IP: " + WiFi.localIP().toString());
}

void reconnect_mqtt() {
  while (!client.connected()) {
    Serial.print("Connecting to MQTT...");
    if (client.connect("ESP32_AirQuality")) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      delay(2000);
    }
  }
}

void setup() {
  Serial.begin(115200);

  pinMode(GREEN_LED, OUTPUT);
  pinMode(BLUE_LED, OUTPUT);
  pinMode(RED_LED, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);

  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("OLED init failed");
    while (true);
  }

  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);
  display.setTextSize(1);
  display.setCursor(0, 0);
  display.println("Air Quality Monitor");
  display.display();

  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
}

void loop() {
  if (!client.connected()) {
    reconnect_mqtt();
  }
  client.loop();

  int mq2Value = analogRead(MQ2_PIN);
  int mq135Value = analogRead(MQ135_PIN);

  String quality;
  // Turn off all LEDs and buzzer first
  digitalWrite(GREEN_LED, LOW);
  digitalWrite(BLUE_LED, LOW);
  digitalWrite(RED_LED, LOW);
  noTone(BUZZER_PIN);

  if (mq2Value < 800) {
    digitalWrite(GREEN_LED, HIGH);
    quality = "GOOD";
  } else if (mq2Value < 1800) {
    digitalWrite(BLUE_LED, HIGH);
    quality = "MODERATE";
  } else {
    digitalWrite(RED_LED, HIGH);
    tone(BUZZER_PIN, 1000);  // 1kHz tone on buzzer
    quality = "BAD";
  }

  // OLED Display
  display.clearDisplay();
  display.setCursor(0, 0);
  display.println("Air Quality Monitor");
  display.setCursor(0, 16);
  display.print("MQ2: ");
  display.println(mq2Value);
  display.setCursor(0, 28);
  display.print("MQ135: ");
  display.println(mq135Value);
  display.setCursor(0, 44);
  display.print("Status: ");
  display.println(quality);
  display.display();

  // MQTT Publish
  char payload[150];
  snprintf(payload, sizeof(payload),
           "{\"mq2\": %d, \"mq135\": %d, \"air_quality\": \"%s\"}",
           mq2Value, mq135Value, quality.c_str());
  client.publish(topic, payload);
  Serial.print("Published: ");
  Serial.println(payload);

  delay(5000);
}
