from telegram import Update
from telegram.ext import ContextTypes
from constants import DB_USERS_PATH, ADMINS
from constants import LAST_ACTIVE_USERS_COUNT
import logging
from database.db_helper import db_execute

logger = logging.getLogger(__name__)


async def admin_show_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in ADMINS:
        logger.info(f"Unauthorized access attempt to admin /show_users by user {user_id}")
        await update.message.reply_text("❌ Neturi teisės.")
        return

    # Gauname paskutinius 50 pagal last_seen (paskutinį aktyvumą)
    users = db_execute("""
        SELECT user_id, username, first_name, last_name, first_seen, last_seen, is_bot
        FROM users
        ORDER BY last_seen DESC
        LIMIT 50
        """,
        fetch='all',
        db_name=DB_USERS_PATH
    )

    # Skaičiuojame bendrą kiekį
    total_count_result = db_execute(
        "SELECT COUNT(*) FROM users",
        fetch='one',
        db_name=DB_USERS_PATH
    )

    total_count = total_count_result[0] if total_count_result else 0

    if not users:
        await update.message.reply_text("📭 Vartotojų nėra.")
        return

    # Formuojame tekstą
    if total_count > LAST_ACTIVE_USERS_COUNT:
        text = f"👥 *Paskutiniai {LAST_ACTIVE_USERS_COUNT} aktyvių vartotojų (iš {total_count}):*\n\n"
    else:
        text = f"👥 *Vartotojų sąrašas ({total_count}):*\n\n"

    for user_id, username, first_name, last_name, first_seen, last_seen, is_bot in users:
        # Suformuojame vardą
        full_name = f"{first_name or ''} {last_name or ''}".strip()
        if not full_name:
            full_name = "Nežinomas"

        # Username
        username_text = f"@{username}" if username else "Be username"

        # Bot emoji
        bot_emoji = "🤖" if is_bot else "👤"

        # Datos su laiku (pakeičiame T į tarpą)
        first_datetime = first_seen[:19].replace("T", " ") if first_seen and len(first_seen) >= 19 else "?"
        last_datetime = last_seen[:19].replace("T", " ") if last_seen and len(last_seen) >= 19 else "?"

        text += f"{bot_emoji} *{full_name}* ({username_text})\n"
        text += f"   ID: `{user_id}`\n\n"
        text += f"   📅 Pirmas: {first_datetime}\n"
        text += f"   📅 Paskutinis: {last_datetime}\n\n"

    await update.message.reply_text(text)
