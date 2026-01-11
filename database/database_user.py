import sqlite3
from config import DB_USERS_PATH


def init_users_database():
    conn = sqlite3.connect(DB_USERS_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT CHECK (LENGTH(username) <= 50),
        first_name TEXT CHECK (LENGTH(first_name) <= 50),
        last_name TEXT CHECK (LENGTH(last_name) <= 50),
        language_code TEXT CHECK (LENGTH(language_code) <= 10),
        is_bot INTEGER DEFAULT 0 CHECK (is_bot IN (0,1)),
        first_seen TEXT DEFAULT CURRENT_TIMESTAMP,
        last_seen TEXT DEFAULT CURRENT_TIMESTAMP,
        is_blocked INTEGER DEFAULT 0 CHECK (is_blocked IN (0,1)),
        total_orders INTEGER DEFAULT 0,
        total_spent REAL DEFAULT 0.0
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

    print("📋 Users DB sukurtos lentelės:")
    for table in tables:
        print(f" - {table[0]}")

    conn.close()
    print("✅ Users duomenų bazė paruošta!")


if __name__ == "__main__":
    init_users_database()
