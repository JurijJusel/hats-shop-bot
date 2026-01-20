import sqlite3
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from constants import DB_PATH


def init_database():
    conn = sqlite3.connect(DB_PATH)  # "shop.db"
    cursor = conn.cursor()

    # Įjungiam foreign key palaikymą
    cursor.execute("PRAGMA foreign_keys = ON;")

    # PRODUCTS (vienetinės kepurės)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL CHECK (LENGTH(name) <= 40),
        description TEXT CHECK (LENGTH(description) <= 1000),
        price REAL NOT NULL CHECK (price >= 0),
        photo_file_id TEXT CHECK (LENGTH(photo_file_id) <= 150),
        category TEXT CHECK (LENGTH(category) <= 20),
        available INTEGER NOT NULL DEFAULT 1 CHECK (available IN (0,1)),
        created_date TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # ORDERS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        user_name TEXT CHECK (LENGTH(user_name) <= 30),
        phone TEXT CHECK (LENGTH(phone) <= 15),
        email TEXT CHECK (LENGTH(email) <= 40),
        info TEXT CHECK (LENGTH(info) <= 500),
        city TEXT CHECK (LENGTH(city) <= 30),
        order_date TEXT DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'naujas',
        total_price REAL CHECK (total_price >= 0),
        payment_info TEXT CHECK (LENGTH(payment_info) <= 200),
        tracking_number TEXT CHECK (LENGTH(tracking_number) <= 50),
        notes TEXT CHECK (LENGTH(notes) <= 500)
    );
    """)

    # ORDER ITEMS (vienetinės prekės)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        product_name TEXT NOT NULL CHECK (LENGTH(product_name) <= 40),
        price_per_unit REAL NOT NULL CHECK (price_per_unit >= 0),
        photo_file_id TEXT CHECK (LENGTH(photo_file_id) <= 150),

        FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products(id)
    );
    """)

    # CART (vienetinės prekės)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cart (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        added_date TEXT DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY (product_id) REFERENCES products(id),
        UNIQUE(user_id, product_id)
    );
    """)
    conn.commit()

    # Atspausdinam lenteles
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table'
        AND name NOT LIKE 'sqlite_%'
        ORDER BY name;
    """)
    tables = cursor.fetchall()

    print("📋 Sukurtos lentelės:")
    for table in tables:
        print(f" - {table[0]}")

    conn.close()
    print("✅ Shop duomenų bazė paruošta!")


if __name__ == "__main__":
    init_database()
