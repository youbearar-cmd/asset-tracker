import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "assets.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        symbol TEXT NOT NULL UNIQUE,
        type TEXT NOT NULL,
        quantity REAL NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS asset_history (
        date TEXT PRIMARY KEY,
        total_value_krw INTEGER NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS asset_details_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        symbol TEXT NOT NULL,
        name TEXT NOT NULL,
        quantity REAL NOT NULL,
        price REAL NOT NULL,
        value_krw INTEGER NOT NULL,
        FOREIGN KEY(date) REFERENCES asset_history(date)
    )
    """)
    # Add index for faster history lookups
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_asset_details_date ON asset_details_history(date)")
    conn.commit()
    conn.close()

def save_daily_history(total_value, asset_details):
    conn = get_db_connection()
    try:
        with conn:
            cursor = conn.cursor()
            from datetime import datetime
            today = datetime.now().strftime("%Y-%m-%d")
            
            # 1. Update/Insert into asset_history
            cursor.execute("""
            INSERT INTO asset_history (date, total_value_krw) VALUES (?, ?)
            ON CONFLICT(date) DO UPDATE SET total_value_krw = excluded.total_value_krw
            """, (today, int(total_value)))
            
            # 2. Delete existing details for today and insert new ones
            cursor.execute("DELETE FROM asset_details_history WHERE date = ?", (today,))
            for a in asset_details:
                cursor.execute("""
                INSERT INTO asset_details_history (date, symbol, name, quantity, price, value_krw)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (today, a['symbol'], a['name'], a['quantity'], a['current_price'], a['value_krw']))
    finally:
        conn.close()

def get_asset_history_details(date):
    """
    Fetches detailed asset snapshot for a specific date.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM asset_details_history WHERE date = ?", (date,))
    details = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return details

def get_asset_history():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM asset_history ORDER BY date ASC")
    history = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return history

def add_asset(name, symbol, asset_type, quantity):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO assets (name, symbol, type, quantity) VALUES (?, ?, ?, ?)",
            (name, symbol, asset_type, quantity)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Update quantity if already exists
        cursor.execute(
            "UPDATE assets SET quantity = quantity + ? WHERE symbol = ?",
            (quantity, symbol)
        )
        conn.commit()
        return True
    finally:
        conn.close()

def get_all_assets():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM assets")
    assets = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return assets

def update_asset_quantity(asset_id, quantity):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE assets SET quantity = ? WHERE id = ?",
        (quantity, asset_id)
    )
    conn.commit()
    conn.close()
    return True

def delete_asset(asset_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM assets WHERE id = ?", (asset_id,))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
