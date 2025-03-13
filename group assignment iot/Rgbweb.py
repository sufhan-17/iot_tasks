import network
import time
import socket
from machine import Pin, I2C
from neopixel import NeoPixel
import dht
import json
from ssd1306 import SSD1306_I2C  # OLED display library
import sys



# ========== 🚀 HARDWARE SETUP ==========
# DHT Sensor
dht_pin = Pin(4, Pin.IN)
dht_sensor = dht.DHT11(dht_pin)

# NeoPixel LED
neo_pin = Pin(48, Pin.OUT)
neo = NeoPixel(neo_pin, 1)

# OLED Display (SCL=9, SDA=8)
i2c = I2C(0, scl=Pin(9), sda=Pin(8))
oled = SSD1306_I2C(128, 64, i2c)

print("✅ OLED Initialized")

# ========== 🌐 WiFi Setup ==========
SSID = "Tenda_1FB6D0"
PASSWORD = "qwerty345"

sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.connect(SSID, PASSWORD)

print("Connecting to WiFi", end="")
for _ in range(10):
    if sta.isconnected():
        break
    print(".", end="")
    time.sleep(1)

if sta.isconnected():
    print("\n✅ Connected to WiFi")
    print("🌍 IP Address (Station Mode):", sta.ifconfig()[0])
else:
    print("\n❌ Failed to connect to WiFi")

# ========== 📡 Access Point Setup ==========
AP_SSID = "ESP32_Server"
AP_PASSWORD = "12345678"
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=AP_SSID, password=AP_PASSWORD, authmode=network.AUTH_WPA2_PSK)

print("✅ Access Point Active")
print("🌍 AP IP Address:", ap.ifconfig()[0])

# ========== 📟 Function to Update OLED ==========
def update_oled(message):
    oled.fill(0)
    oled.text(message, 0, 0)
    oled.show()
    
    

# ========== 🌍 Web Page HTML ==========
# ========== 🌍 Web Page HTML (With Sensor Data) ==========
def web_page():
    try:
        dht_sensor.measure()  # Read data from DHT11
        temp = dht_sensor.temperature()
        humidity = dht_sensor.humidity()
    except:
        temp = "N/A"
        humidity = "N/A"

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>ESP32 Web Server</title>
    <style>
        body {{ font-family: Arial; text-align: center; background: black; color: orange; }}
        h1 {{ color: orange; text-shadow: 0px 0px 10px orange; }}
        button {{ padding: 10px; margin: 10px; font-size: 16px; border-radius: 10px; border: none; cursor: pointer; }}
        .sensor {{ background: #222; padding: 15px; border-radius: 10px; border: 2px solid orange; }}
        .btn-red {{ background: red; color: white; }}
        .btn-green {{ background: green; color: white; }}
        .btn-blue {{ background: blue; color: white; }}
    </style>
</head>
<body>
    <h1>🔥 ESP32 Web Server 🔥</h1>
    <div class="sensor">
        <h2>Temperature: <span id="temp">{temp}</span>°C</h2>
        <h2>Humidity: <span id="humidity">{humidity}</span>%</h2>
    </div>
    <br>
    <h2>RGB LED Control</h2>
    <button class="btn-red" onclick="location.href='/?RGB=red'">RED</button>
    <button class="btn-green" onclick="location.href='/?RGB=green'">GREEN</button>
    <button class="btn-blue" onclick="location.href='/?RGB=blue'">BLUE</button>
    <br>
    <h2>Custom Color</h2>
    <form action="/" method="GET">
        R: <input type="number" name="R" min="0" max="255" value="0">
        G: <input type="number" name="G" min="0" max="255" value="0">
        B: <input type="number" name="B" min="0" max="255" value="0">
        <input type="submit" value="Set Color">
    </form>
    <br>
    <h2>OLED Display</h2>
    <form action="/">
        <input name="msg" type="text" placeholder="Enter text">
        <input type="submit" value="Send">
    </form>
    <p style="text-align:center;">&copy; All rights reserved by Faisal Chan | Sufhan Siddique | Abdul Rafay</p>

</body>
</html>"""
    return html

# ========== 🌍 Web Server ==========
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Fix address reuse issue
server.bind(("0.0.0.0", 80))
server.listen(5)

print("✅ Web Server Running")
print("🌐 Open in browser:", sta.ifconfig()[0])

while True:
    try:
        conn, addr = server.accept()
        print("🔗 Connection from:", addr)
        request = conn.recv(1024).decode()

        # ========== 🌈 RGB LED Control ==========
        if "/?RGB=red" in request:
            neo[0] = (255, 0, 0)  # Red
            neo.write()
        elif "/?RGB=green" in request:
            neo[0] = (0, 255, 0)  # Green
            neo.write()
        elif "/?RGB=blue" in request:
            neo[0] = (0, 0, 255)  # Blue
            neo.write()
        elif "?R=" in request and "&G=" in request and "&B=" in request:
            try:
                r = int(request.split("R=")[1].split("&")[0])
                g = int(request.split("G=")[1].split("&")[0])
                b = int(request.split("B=")[1].split(" ")[0])
                neo[0] = (r, g, b)
                neo.write()
            except:
                print("⚠ Error parsing RGB values")

        # ========== 📟 OLED Display Control ==========
        elif "msg=" in request:
            try:
                msg = request.split("msg=")[1].split("&")[0]
                update_oled(msg)
            except:
                print("⚠ Error processing OLED message")

        # ========== 🌍 Serve Web Page ==========
        response = web_page()
        
        conn.send("HTTP/1.1 200 OK\nContent-Type: text/html\nConnection: close\n\n")
        conn.sendall(response)
        conn.close()
    
    except Exception as e:
        print("⚠ Server error:", e)
