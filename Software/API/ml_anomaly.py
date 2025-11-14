import os
import sqlite3
import numpy as np

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "Database", "energy_data.db")
DB_PATH = os.path.abspath(DB_PATH)

def get_device_data(device):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT ts, power_w FROM measurements WHERE lower(device) = ? ORDER BY ts ASC",
        (device.lower(),)
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def detect_anomalies(device):
    rows = get_device_data(device)
    if not rows:
        return []

    timestamps = np.array([r[0] for r in rows])   # epoch timestamps
    values = np.array([r[1] for r in rows])       # power readings

    mean = np.mean(values)
    std = np.std(values)

    # Handle zero-std case: no anomalies unless values differ
    if std == 0:
        return []

    z_scores = (values - mean) / std
    THRESHOLD = 2.5  # softer threshold for your simulated data
    anomaly_indices = np.where(z_scores > THRESHOLD)[0]

    anomalies = []
    for idx in anomaly_indices:
        anomalies.append({
            "timestamp": int(timestamps[idx]),
            "power_w": float(values[idx]),
            "z_score": float(z_scores[idx])
        })

    return anomalies