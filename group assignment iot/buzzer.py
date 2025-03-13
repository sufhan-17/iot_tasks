import network
import socket
from machine import Pin
from neopixel import NeoPixel

# WiFi Credentials
SSID = "Tenda_1FB6D0"
PASSWORD = "qwerty345"

# NeoPixel RGB LED Setup
neo_pin = Pin(48, Pin.OUT)
neo = NeoPixel(neo_pin, 1)

# Connect to WiFi
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.connect(SSID, PASSWORD)
while not sta.isconnected():
    pass
print("Connected to WiFi", sta.ifconfig()[0])

# Web Page with Color Picker
def web_page():
    return """<!DOCTYPE html>
<html>
<head>
    <title>ESP32 Color Picker</title>
    <style>
        body { font-family: Arial; text-align: center; background: black; color: orange; }
        h1 { color: orange; }
    </style>
</head>
<body>
    <h1>ESP32 Color Picker</h1>
    <input type="color" id="colorPicker">
    <button onclick="sendColor()">Set Color</button>
    <script>
        function sendColor() {
            let color = document.getElementById('colorPicker').value.substring(1);
            let r = parseInt(color.substr(0,2), 16);
            let g = parseInt(color.substr(2,2), 16);
            let b = parseInt(color.substr(4,2), 16);
            fetch(`/?R=${r}&G=${g}&B=${b}`);
        }
    </script>
</body>
</html>"""

# Web Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("0.0.0.0", 80))
server.listen(5)

while True:
    conn, addr = server.accept()
    request = conn.recv(1024).decode()
    
    if "?R=" in request and "&G=" in request and "&B=" in request:
        try:
            r = int(request.split("R=")[1].split("&")[0])
            g = int(request.split("G=")[1].split("&")[0])
            b = int(request.split("B=")[1].split(" ")[0])
            neo[0] = (r, g, b)
            neo.write()
        except:
            pass
    
    response = web_page()
    conn.send("HTTP/1.1 200 OK\nContent-Type: text/html\nConnection: close\n\n")
    conn.sendall(response)
    conn.close()
