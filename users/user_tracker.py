import sqlite3
from datetime import datetime
from telegram import Update
from config import DB_USERS_PATH, ADMINS


def register_or_update_user(update: Update):
    """Užregistruoja arba atnaujina vartotojo info"""
    user = update.effective_user

    # Neregistruoti, jei nėra vartotojo arba jei tai admin
    if not user or user.id in ADMINS:
        return

    conn = sqlite3.connect(DB_USERS_PATH)
    cursor = conn.cursor()

    # Patikrinam, ar vartotojas jau yra
    cursor.execute("SELECT user_id FROM users WHERE user_id=?", (user.id,))
    exists = cursor.fetchone()

    now = datetime.now().isoformat()

    if exists:
        # Atnaujinam last_seen ir kitus duomenis
        cursor.execute("""
            UPDATE users
            SET last_seen=?, username=?, first_name=?, last_name=?, is_bot=?
            WHERE user_id=?
        """, (
            now,
            user.username,
            user.first_name,
            user.last_name,
            1 if user.is_bot else 0,
            user.id
            )
        )
    else:
        # Sukuriame naują
        cursor.execute("""
            INSERT INTO users
            (user_id, username, first_name, last_name, language_code, is_bot, first_seen, last_seen)
            VALUES (?,?,?,?,?,?,?,?)
        """, (
            user.id,
            user.username,
            user.first_name,
            user.last_name,
            user.language_code,
            1 if user.is_bot else 0,
            now,
            now
            )
        )

    conn.commit()
    conn.close()
