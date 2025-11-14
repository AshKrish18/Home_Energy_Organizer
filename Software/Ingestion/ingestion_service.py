import json
import sqlite3
import paho.mqtt.client as mqtt
from datetime import datetime

# --- DB Setup ---
DB_PATH = "/Users/ashkrish18/Documents/Coding/Project/Home_Energy_Organizer/energy_data.db" 
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS measurements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT,
    device TEXT,
    power_w REAL
)
""")
conn.commit()

# --- MQTT Callback ---
def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        ts = datetime.fromtimestamp(data["timestamp"])
        device = data["device"]
        power = data["power_w"]

        cursor.execute(
            "INSERT INTO measurements (ts, device, power_w) VALUES (?, ?, ?)",
            (ts, device, power)
        )
        conn.commit()

        print(f"✅ Saved: {device} {power}W at {ts}")
    except Exception as e:
        print(f"❌ Error: {e}")

# --- MQTT Setup ---
client = mqtt.Client()
client.on_message = on_message

client.connect("localhost", 1883, 60)
client.subscribe("home/#")

print("📡 Ingestion service started... Listening to home/#")
client.loop_forever()