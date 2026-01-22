import sqlite3
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from constants import DB_BANNED_USERS


def init_users_database():
    conn = sqlite3.connect(DB_BANNED_USERS)  # "banned_users.db"
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blacklist (
            user_id INTEGER PRIMARY KEY,
            ban_date TEXT DEFAULT CURRENT_TIMESTAMP,
            banned_by INTEGER NOT NULL
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

    print("📋 Blacklist DB sukurtos lentelės:")
    for table in tables:
        print(f" - {table[0]}")

    conn.close()
    print("✅ Blacklist duomenų bazė paruošta!")


def main():
    init_users_database()

if __name__ == "__main__":
    main()
