import logging
import sqlite3
from telegram import Update
from telegram.ext import ContextTypes
from constants import ADMINS, DB_BANNED_USERS
from functools import wraps

logger = logging.getLogger(__name__)


# ===== FUNKCIJA: Patikrinti ar user'is blacklist'e =====
def is_user_banned(user_id: int) -> bool:
    """Tikrina ar user_id yra blacklist lentelėje"""
    with sqlite3.connect(DB_BANNED_USERS) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM blacklist WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        return result is not None


def check_blacklist(func):
    """
    Decorator'ius tikrinti ar user'is užbanintas.
    Jei taip - sustabdo funkcijos vykdymą ir parodo pranešimą.

    Naudojimas:
    @check_blacklist
    async def tavo_funkcija(update, context):
    """
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        # Gauti user_id iš message arba callback_query
        if update.message:
            user_id = update.message.from_user.id
        elif update.callback_query:
            user_id = update.callback_query.from_user.id
        else:
            # Jei nėra nei message, nei callback - leisti toliau
            return await func(update, context, *args, **kwargs)

        # Patikrinti blacklist
        if is_user_banned(user_id):
            logger.info(f"Banned user {user_id} tried to use {func.__name__}")

            message_text = (
                "🚫 Jūs esate užblokuotas ir negalite naudotis botu.\n"
                "Dėl informacijos kreipkitės į administratorių."
            )

            # Atsakyti priklausomai nuo tipo
            if update.message:
                await update.message.reply_text(message_text)
            elif update.callback_query:
                await update.callback_query.answer(
                    "🚫 Jūs esate užblokuotas!",
                    show_alert=True
                )

            return

        return await func(update, context, *args, **kwargs)

    return wrapper


# ===== KOMANDA: /ban_user =====
async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Admin komanda užbaninti userį
        Naudojimas: /ban_user 123456789
    """
    user = update.effective_user
    admin_id = user.id
    username = user.username

    if admin_id not in ADMINS:
        user_info = f"@{username}" if username else f"ID:{admin_id}"
        logger.info(f"Neautorizuotas bandymas prieiti prie /ban_user. User: {user_info}")
        await update.message.reply_text("❌ Neturi teisės naudoti šios komandos.")
        return

    # Patikrinti ar yra argumentas (user_id)
    if not context.args:
        await update.message.reply_text("❌ Naudojimas: /ban_user <user_id>")
        return

    try:
        user_to_ban = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ User ID turi būti skaičius!")
        return

    # Patikrinti ar jau užbanintas
    if is_user_banned(user_to_ban):
        await update.message.reply_text(f"⚠️ User {user_to_ban} jau yra ban liste!")
        return

    # Įrašyti į blacklist
    with sqlite3.connect(DB_BANNED_USERS) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO blacklist (user_id, banned_by) VALUES (?, ?)",
                (user_to_ban, admin_id)
            )
            conn.commit()
            await update.message.reply_text(f"✅ User {user_to_ban} užbanintas!")
        except sqlite3.Error as e:
            await update.message.reply_text(f"❌ Klaida: {e}")


# ===== KOMANDA: /unban_user =====
async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Admin komanda išimti userį iš blacklist
        Naudojimas: /unban_user 123456789
    """
    user = update.effective_user
    admin_id = user.id
    username = user.username

    # Patikrinti ar user'is yra admin'as
    if admin_id not in ADMINS:
        user_info = f"@{username}" if username else f"ID:{admin_id}"
        logger.info(f"Neautorizuotas bandymas prieiti prie /unban_user. User: {user_info}")
        await update.message.reply_text("❌ Neturi teisės naudoti šios komandos.")
        return

    # Patikrinti ar yra argumentas (user_id)
    if not context.args:
        await update.message.reply_text("❌ Naudojimas: /unban_user <user_id>")
        return

    try:
        user_to_unban = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ User ID turi būti skaičius!")
        return

    # Patikrinti ar user'is yra blacklist'e
    if not is_user_banned(user_to_unban):
        await update.message.reply_text(f"⚠️ User {user_to_unban} nėra ban liste!")
        return

    # Ištrinti iš blacklist
    with sqlite3.connect(DB_BANNED_USERS) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM blacklist WHERE user_id = ?", (user_to_unban,))
            conn.commit()
            await update.message.reply_text(f"✅ User {user_to_unban} pašalintas iš ban listo!")
        except sqlite3.Error as e:
            await update.message.reply_text(f"❌ Klaida: {e}")
