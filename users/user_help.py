from telegram import Update
from telegram.ext import ContextTypes
from admin.admin_ban_user import check_blacklist


@check_blacklist
async def user_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    info_text = (
        "📋 Prieinamos komandos:\n\n"
        "/help - parodyti šį meniu\n"
        "/my_orders - peržiūrėti mano užsakymus\n"
        "/cancel - atšaukti užsakymą"
    )

    await update.message.reply_text(info_text)
