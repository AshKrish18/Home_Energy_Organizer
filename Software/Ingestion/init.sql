-- init.sql
-- Schema for energy data storage

CREATE TABLE IF NOT EXISTS measurements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TIMESTAMP,
    device TEXT,
    power_w REAL
);