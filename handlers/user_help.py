from telegram import Update
from telegram.ext import ContextTypes


async def user_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    info_text = (
        "📋 Prieinamos komandos:\n\n"
        "/cancel - atšaukti užsakymą\n"
        "/my_orders - peržiūrėti mano užsakymus\n"
        "/help - parodyti šį meniu"
    )

    await update.message.reply_text(info_text)
