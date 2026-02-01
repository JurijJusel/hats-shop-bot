from telegram import Update
from telegram.ext import ContextTypes
from admin.admin_ban_user import check_blacklist


@check_blacklist
async def user_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    info_text = (
        "📋 Prieinamos komandos:\n\n"
        "/my_orders - peržiūrėti mano užsakymus\n"
        "/cancel - atšaukti užsakymą\n"
        "/klausimai - dažniausiai užduodami klausimai ir kontaktai\n"
        "/help - parodyti šį meniu\n"
    )

    await update.message.reply_text(info_text)
