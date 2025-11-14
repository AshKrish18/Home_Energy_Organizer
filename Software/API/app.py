from fastapi import FastAPI
import sqlite3
from typing import List, Dict
from fastapi.middleware.cors import CORSMiddleware
from ml_anomaly import detect_anomalies
from ml_predict import predict_next_value, predict_next_hour_sum

#uvicorn app:app --reload --port 8000 Use this to activate api

app = FastAPI(title="Home Energy Optimizer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can restrict to ["http://127.0.0.1:8000"] if using Live Server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "/Users/ashkrish18/Documents/Coding/Project/Home_energy_organizer/energy_data.db"  # adjust if needed

# Helper function to query DB
def query_db(query: str, params: tuple = ()) -> List[Dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.get("/readings/latest")
def get_latest_readings():
    rows = query_db(
        """
        SELECT m.*
        FROM measurements m
        INNER JOIN (
            SELECT device, MAX(ts) AS latest_ts
            FROM measurements
            WHERE device IN ('fridge', 'washer', 'ac', 'lights')
            GROUP BY device
        ) latest
        ON m.device = latest.device AND m.ts = latest.latest_ts
        ORDER BY m.device
        """
    )
    return {"readings": rows}




# Root
@app.get("/")
def home():
    return {"message": "Home Energy Optimizer API is running 🚀"}


# Get all devices
@app.get("/devices")
def get_devices():
    rows = query_db("SELECT DISTINCT device FROM measurements")
    return {"devices": [row["device"] for row in rows]}


# Get last N readings
@app.get("/readings/{device}")
def get_readings(device: str, limit: int = 10):
    rows = query_db(
        "SELECT * FROM measurements WHERE device = ? ORDER BY ts DESC LIMIT ?",
        (device, limit),
    )
    return {"device": device, "readings": rows}


# Get today’s usage (sum)
@app.get("/usage/total")
def get_total_usage():
    rows = query_db(
        "SELECT SUM(power_w) as total_consumption FROM measurements WHERE DATE(ts) = DATE('now')"
    )
    return {"total_consumption": rows[0]["total_consumption"] if rows and rows[0]["total_consumption"] else 0}
#Run uvicorn app:app --reload --port 8000 to restart the fastapi
# Daily usage (last 7 days)
@app.get("/usage/daily")
def get_daily_usage():
    rows = query_db("""
        SELECT DATE(ts, 'unixepoch') as day, SUM(power_w) as total
        FROM measurements
        GROUP BY day
        ORDER BY day DESC
        LIMIT 7
    """)
    return {"daily": rows[::-1]}  # reverse so oldest -> newest


# Monthly usage (last 6 months)
@app.get("/usage/monthly")
def get_monthly_usage():
    rows = query_db("""
        SELECT strftime('%Y-%m', ts, 'unixepoch') as month, SUM(power_w) as total
        FROM measurements
        GROUP BY month
        ORDER BY month DESC
        LIMIT 6
    """)
    return {"monthly": rows[::-1]}

@app.get("/anomalies")
def get_anomaly_report():
    devices = ["fridge", "washer", "ac", "lights"]
    report = {}

    for d in devices:
        report[d] = detect_anomalies(d)

    return {"anomalies": report}

@app.get("/predict/next")
def predict_next():
    value, ts = predict_next_value()
    return {"timestamp": ts, "predicted_power": value}


@app.get("/predict/next_hour")
def predict_hour():
    prediction = predict_next_hour_sum()
    return {"predicted_hourly_usage": prediction}