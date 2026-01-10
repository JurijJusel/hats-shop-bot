from telegram import Update
from telegram.ext import ContextTypes
from config import ADMINS


async def admin_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in ADMINS:
        await update.message.reply_text("❌ Neturi teisės matyti komandų.")
        return

    info_text = (
        "📋 Prieinamos ADMIN komandos:\n\n"
        "/add_hat - pridėti naują kepurę\n"
        "/show_hats - peržiūrėti visus produktus\n"
        "/show_orders - peržiūrėti visus užsakymus su statusais ir mygtukais\n"
        "/show_orders_10 - peržiūrėti paskutinius 10 užsakymų\n"
        "/show_orders_status - peržiūrėti paskutinius neuzbaigtu užsakymų\n"
        "/show_users - peržiūrėti paskutinius 50 aktyvių vartotojų\n"
        "/info - parodyti šį meniu"
    )

    await update.message.reply_text(info_text)
