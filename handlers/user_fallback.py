from telegram import Update
from telegram.ext import ContextTypes
from config import ADMINS


async def unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Fallback handler - kai vartotojas įveda tekstą, kuris nėra komanda.
    Admin'ai ignoruojami - jie gali rašyti tekstą laisvai.
    """
    user_id = update.message.from_user.id

    # Jei admin - ignoruojam (adminas gali rašyti tekstą)
    if user_id in ADMINS:
        return

    # Vartotojui - draugiškas pranešimas
    await update.message.reply_text(
        "🤖 Labas! Suprantu tik komandas.\n\n"
        "📋 Rodyti komandas: /help\n"
        "🛍 Peržiūrėti prekes: /start"
    )
