import json
from paho.mqtt import client as mqtt_client
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# MQTT broker config
broker = '172.20.10.8'  # HiveMQ IP
port = 1883
topic = "esp32/air_quality"
client_id = 'mqtt_influx_bridge'

# InfluxDB config
influx_url = "http://localhost:8086"
token = "R5pxqAZrrxiCgsCexGALmwG2PeVaGyqNsMpPAfSy89ufz6z8QuvZCKvz3qlHKaGGILdxkqvf17FkIIlvY9hetw=="
org = "ntu"
bucket = "air_quality_monitor"

# Initialize InfluxDB client
influx_client = InfluxDBClient(url=influx_url, token=token, org=org)
write_api = influx_client.write_api(write_options=SYNCHRONOUS)

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print(f"Failed to connect, return code {rc}")

    client = mqtt_client.Client(client_id=client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client



def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        data = json.loads(payload)
        print(f"Received MQTT data: {data}")

        # Prepare InfluxDB point
        point = (
            Point("air_quality")
            .field("mq2", int(data.get("mq2", 0)))
            .field("mq135", int(data.get("mq135", 0)))
            .tag("quality", data.get("air_quality", "UNKNOWN"))
        )

        # Write to InfluxDB
        write_api.write(bucket=bucket, org=org, record=point)
        print("Written to InfluxDB")
    except Exception as e:
        print(f"Error processing message: {e}")

def run():
    client = connect_mqtt()
    client.subscribe(topic)
    client.on_message = on_message
    client.loop_forever()

if __name__ == '__main__':
    run()
