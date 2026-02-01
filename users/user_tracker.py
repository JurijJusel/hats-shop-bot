from datetime import datetime
from telegram import Update
from constants import DB_USERS_PATH, ADMINS
import logging
from database.db_helper import db_execute

logger = logging.getLogger(__name__)


def register_or_update_user(update: Update):
    """Užregistruoja arba atnaujina vartotojo info"""
    user = update.effective_user

    # Neregistruoti, jei nėra vartotojo arba jei tai admin
    if not user or user.id in ADMINS:
        return

    # Patikrinam, ar vartotojas jau yra
    user_exists = db_execute(
        "SELECT user_id FROM users WHERE user_id=?",
        (user.id,),
        fetch='one',
        db_name=DB_USERS_PATH
    )

    now = datetime.now().isoformat()

    if user_exists:
        # Atnaujinam last_seen ir kitus duomenis
        success = db_execute(
            """
            UPDATE users
            SET last_seen=?, username=?, first_name=?, last_name=?, is_bot=?
            WHERE user_id=?
            """,
            (
                now,
                user.username,
                user.first_name,
                user.last_name,
                1 if user.is_bot else 0,
                user.id
            )
        )

        if success:
            logger.info(f"User activity updated {user.id} - (@{user.username or 'no_username'})")
        else:
            logger.error(f"Failed to update user activity: {user.id}")

    else:
        # Sukuriame naują
        success = db_execute(
            """
            INSERT INTO users
            (user_id, username, first_name, last_name, language_code, is_bot, first_seen, last_seen)
            VALUES (?,?,?,?,?,?,?,?)
            """,
            (
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

        if success:
            logger.info(f"New user registered: {user.id} - (@{user.username or 'no_username'})")
        else:
            logger.error(f"Failed to register new user: {user.id}")
