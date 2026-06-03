import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")


def get_db_connection():
    url = DATABASE_URL
    # Supabase uses postgres:// but psycopg2 requires postgresql://
    if url and url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    conn = psycopg2.connect(url, sslmode="require")
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assets (
        id SERIAL PRIMARY KEY,
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
        id SERIAL PRIMARY KEY,
        date TEXT NOT NULL,
        symbol TEXT NOT NULL,
        name TEXT NOT NULL,
        quantity REAL NOT NULL,
        price REAL NOT NULL,
        value_krw INTEGER NOT NULL,
        FOREIGN KEY(date) REFERENCES asset_history(date)
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_asset_details_date ON asset_details_history(date)")
    conn.commit()
    cursor.close()
    conn.close()


def save_daily_history(total_value, asset_details):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")

        cursor.execute("""
        INSERT INTO asset_history (date, total_value_krw) VALUES (%s, %s)
        ON CONFLICT(date) DO UPDATE SET total_value_krw = EXCLUDED.total_value_krw
        """, (today, int(total_value)))

        cursor.execute("DELETE FROM asset_details_history WHERE date = %s", (today,))
        for a in asset_details:
            cursor.execute("""
            INSERT INTO asset_details_history (date, symbol, name, quantity, price, value_krw)
            VALUES (%s, %s, %s, %s, %s, %s)
            """, (today, a['symbol'], a['name'], a['quantity'], a['current_price'], a['value_krw']))

        conn.commit()
        cursor.close()
    finally:
        conn.close()


def get_asset_history_details(date):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM asset_details_history WHERE date = %s", (date,))
    details = [dict(row) for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return details


def get_asset_history():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM asset_history ORDER BY date ASC")
    history = [dict(row) for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return history


def add_asset(name, symbol, asset_type, quantity):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO assets (name, symbol, type, quantity) VALUES (%s, %s, %s, %s)",
            (name, symbol, asset_type, quantity)
        )
        conn.commit()
        return True
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        cursor.execute(
            "UPDATE assets SET quantity = quantity + %s WHERE symbol = %s",
            (quantity, symbol)
        )
        conn.commit()
        return True
    finally:
        cursor.close()
        conn.close()


def get_all_assets():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM assets")
    assets = [dict(row) for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return assets


def update_asset_quantity(asset_id, quantity):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE assets SET quantity = %s WHERE id = %s",
        (quantity, asset_id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return True


def delete_asset(asset_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM assets WHERE id = %s", (asset_id,))
    conn.commit()
    cursor.close()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized.")
