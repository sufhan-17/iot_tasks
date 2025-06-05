import time
import ssd1306
import _thread
import machine
from machine import Pin, SoftI2C
from umqtt.simple import MQTTClient

# ----- CONFIG -----
I2C_SCL = 9
I2C_SDA = 8
THINGSPEAK_MQTT_HOST = "mqtt3.thingspeak.com"
THINGSPEAK_MQTT_PORT = 1883
THINGSPEAK_CHANNEL_ID = "2924683"
THINGSPEAK_CLIENT_ID = "ATU5NAQcMB0hJysvOQ07Oz0"
THINGSPEAK_USERNAME = "ATU5NAQcMB0hJysvOQ07Oz0"
THINGSPEAK_MQTT_API_KEY = "qxs9yCwCuC4urJYE2OP59OQU"

MQTT_SUB_TOPIC = f"channels/{THINGSPEAK_CHANNEL_ID}/subscribe/fields/field1/{THINGSPEAK_MQTT_API_KEY}"
MQTT_SUB_TOPIC_HUM = f"channels/{THINGSPEAK_CHANNEL_ID}/subscribe/fields/field2/{THINGSPEAK_MQTT_API_KEY}"

# ----- INIT -----
i2c = SoftI2C(scl=Pin(I2C_SCL), sda=Pin(I2C_SDA))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)
lock = _thread.allocate_lock()

# Shared Data
shared = {
    "temp": "--",
    "hum": "--"
}

# ----- OLED LOOP -----
def oled_loop():
    while True:
        lock.acquire()
        temp = shared["temp"]
        hum = shared["hum"]
        lock.release()

        oled.fill(0)
        oled.text("MQTT Receiver", 0, 0)
        oled.text("Temp: {} C".format(temp), 0, 16)
        oled.text("Hum : {} %".format(hum), 0, 32)
        oled.show()
        time.sleep(1)

# ----- MQTT CALLBACK -----
def mqtt_callback(topic, msg):
    topic_str = topic.decode()
    msg_str = msg.decode()
    print("Received:", topic_str, msg_str)

    lock.acquire()
    if "field1" in topic_str:
        shared["temp"] = msg_str
    elif "field2" in topic_str:
        shared["hum"] = msg_str
    lock.release()

# ----- MQTT INIT + LOOP -----
def connect_mqtt():
    try:
        client = MQTTClient(client_id=THINGSPEAK_CLIENT_ID,
                            server=THINGSPEAK_MQTT_HOST,
                            port=THINGSPEAK_MQTT_PORT,
                            user=THINGSPEAK_USERNAME,
                            password=THINGSPEAK_MQTT_API_KEY)
        
        client.set_callback(mqtt_callback)
        client.connect()
        print("Connected to MQTT broker.")

        client.subscribe(MQTT_SUB_TOPIC)
        client.subscribe(MQTT_SUB_TOPIC_HUM)
        print("Subscribed to:", MQTT_SUB_TOPIC, "and", MQTT_SUB_TOPIC_HUM)

        return client
    except Exception as e:
        print("MQTT connect failed:", e)
        return None

def main_loop():
    client = connect_mqtt()
    if not client:
        print("MQTT failed. Rebooting...")
        time.sleep(5)
        machine.reset()

    while True:
        try:
            client.check_msg()
        except Exception as e:
            print("MQTT check_msg error:", e)
        time.sleep(1)

# ----- START -----
print("Starting OLED on Core 1...")
_thread.start_new_thread(oled_loop, ())

print("Running MQTT Subscriber on Core 0...")
main_loop()