import sqlite3
import os
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "mebel.db")

DEFAULT_SETTINGS = {
    "ldsp_cost":  45_000,   # so'm / m²
    "mdf_cost":   65_000,   # so'm / m²
    "xdf_cost":   12_000,   # so'm / m²  (orqa panel)
    "edge_cost":   2_500,   # so'm / metr (qirra lenta)
    "hinge_cost":  5_000,   # so'm / dona (petlya)
    "handle_cost": 8_000,   # so'm / dona (tutqich)
    "screw_cost": 15_000,   # so'm / to'plam (vintlar)
    "ldsp_sell": 130_000,   # sotish narxi so'm / m²
    "mdf_sell":  190_000,   # sotish narxi so'm / m²
}

SETTING_LABELS = {
    "ldsp_cost":  "LDSP xarajati (so'm/m²)",
    "mdf_cost":   "MDF xarajati (so'm/m²)",
    "xdf_cost":   "XDF xarajati (so'm/m²)",
    "edge_cost":  "Qirra lenta (so'm/m)",
    "hinge_cost": "Petlya (so'm/dona)",
    "handle_cost":"Tutqich (so'm/dona)",
    "screw_cost": "Vintlar to'plami (so'm)",
    "ldsp_sell":  "LDSP sotish narxi (so'm/m²)",
    "mdf_sell":   "MDF sotish narxi (so'm/m²)",
}


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS settings (
        key   TEXT PRIMARY KEY,
        value REAL NOT NULL
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS calculations (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp    TEXT NOT NULL,
        user_id      INTEGER NOT NULL,
        user_name    TEXT,
        furniture    TEXT,
        material     TEXT,
        width        REAL,
        height       REAL,
        depth        REAL,
        extra        TEXT,
        body_area    REAL,
        xdf_area     REAL,
        edge_meters  REAL,
        hinges       INTEGER,
        handles      INTEGER,
        screw_sets   INTEGER,
        mat_cost     REAL,
        sell_price   REAL,
        profit       REAL,
        profit_pct   REAL
    )""")

    for k, v in DEFAULT_SETTINGS.items():
        c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (k, v))

    conn.commit()
    conn.close()


def get_settings() -> dict:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT key, value FROM settings").fetchall()
    conn.close()
    return {k: v for k, v in rows}


def update_setting(key: str, value: float):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE settings SET value=? WHERE key=?", (value, key))
    conn.commit()
    conn.close()


def save_calc(user_id, user_name, furniture, material,
              width, height, depth, extra,
              body_area, xdf_area, edge_meters,
              hinges, handles, screw_sets,
              mat_cost, sell_price, profit, profit_pct):
    ts = (datetime.utcnow() + timedelta(hours=5)).strftime("%d.%m.%Y %H:%M")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""INSERT INTO calculations
        (timestamp,user_id,user_name,furniture,material,
         width,height,depth,extra,
         body_area,xdf_area,edge_meters,hinges,handles,screw_sets,
         mat_cost,sell_price,profit,profit_pct)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (ts, user_id, user_name, furniture, material,
         width, height, depth, extra,
         body_area, xdf_area, edge_meters, hinges, handles, screw_sets,
         mat_cost, sell_price, profit, profit_pct))
    conn.commit()
    conn.close()


def get_recent(limit=20):
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT * FROM calculations ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return rows


def get_all():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT * FROM calculations ORDER BY id DESC").fetchall()
    conn.close()
    return rows
