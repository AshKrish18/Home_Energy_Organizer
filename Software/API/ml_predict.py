import os
import sqlite3
import numpy as np
from sklearn.linear_model import LinearRegression
import datetime

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Database", "energy_data.db"))

def get_total_usage_data():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute("""
        SELECT ts, power_w
        FROM measurements
        ORDER BY ts ASC
    """)
    rows = cur.fetchall()
    conn.close()

    if not rows:
        return None, None

    timestamps = np.array([r[0] for r in rows]).reshape(-1, 1)  # X
    power = np.array([r[1] for r in rows])  # y

    return timestamps, power


def predict_next_value():
    X, y = get_total_usage_data()
    if X is None:
        return None
    
    model = LinearRegression()
    model.fit(X, y)

    next_ts = np.array([[int(X[-1][0] + 300)]])  # predict next 5 mins

    prediction = model.predict(next_ts)[0]
    return float(prediction), int(next_ts[0][0])


def predict_next_hour_sum():
    predictions = []
    X, _ = get_total_usage_data()
    if X is None:
        return 0
    
    last_ts = int(X[-1][0])

    model = LinearRegression()
    model.fit(X, y)

    for i in range(12):  # 12 predictions × 5 minutes = 1 hour
        next_ts = np.array([[last_ts + (i+1)*300]])
        predictions.append(model.predict(next_ts)[0])

    return float(sum(predictions))