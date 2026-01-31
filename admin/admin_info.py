import logging
from telegram import Update
from telegram.ext import ContextTypes
from constants import ADMINS

logger = logging.getLogger(__name__)


async def admin_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    username = user.username

    if user_id not in ADMINS:

        user_info = f"@{username}" if username else f"ID:{user_id}"
        logger.info(f"Neautorizuotas bandymas prieiti prie /info. User: {user_info}")

        await update.message.reply_text("❌ Neturi teisės matyti komandų.")
        return

    info_text = (
        "📋 Prieinamos ADMIN komandos:\n\n"
        "/add_hat - pridėti naują kepurę\n"
        "/show_hats - peržiūrėti visus produktus\n"
        "/show_orders - peržiūrėti visus užsakymus su statusais ir mygtukais\n"
        "/show_orders_10 - peržiūrėti paskutinius 10 užsakymų\n"
        "/show_orders_status - peržiūrėti paskutinius neužbaigtų užsakymų\n"
        "/show_users - peržiūrėti paskutinius 20 aktyvių vartotojų\n"
        "/ban_user - užbaninti vartotoją (pvz: /ban_user 1234567890)\n"
        "/unban_user - atbaninti vartotoją (pvz: /unban_user 1234567890)\n"
        "/info - parodyti šį meniu"
    )

    await update.message.reply_text(info_text)
