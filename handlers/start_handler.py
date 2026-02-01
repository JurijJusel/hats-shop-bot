from telegram import (Update,
                    InlineKeyboardButton,
                    InlineKeyboardMarkup,
                    ReplyKeyboardMarkup,
                    KeyboardButton)
from telegram.ext import ContextTypes
from constants import DB_PATH
from users.user_tracker import register_or_update_user
from admin.admin_ban_user import check_blacklist
import logging
from database.db_helper import db_execute

logger = logging.getLogger(__name__)


# Fiksuotas klaviatūros meniu apacioje
@check_blacklist
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_or_update_user(update)  # Registruoti arba atnaujinti user'io duomenis

    logger.info(f"User {update.message.from_user.id} started bot")

    keyboard = [
        [KeyboardButton("🧢 Kepurės"), KeyboardButton("🛒 Krepšelis")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Sveiki! Aš esu 'Felting Hats Shop' asistentas. Pasirinkite veiksmą iš meniu apačioje 👇",
        reply_markup=reply_markup
    )


# Tekstinis mygtukas "🧢 Kepurės"
@check_blacklist
async def text_show_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    products = db_execute(
        "SELECT id, name, description, price, photo_file_id FROM products WHERE available = 1",
        fetch='all',
        db_name=DB_PATH
    )

    if not products:
        logger.info("No products available when user requested catalog")
        await update.message.reply_text("❌ Šiuo metu produktų nėra.")
        return

    for prod in products:
        prod_id, name, description, price, photo = prod

        caption = (
            f"\u2800\u2800\u2800{name}\n\n"
            f"📝  Info: {description}\n\n"
            f"💰 Kaina: {price:.2f}€"
        )

        keyboard = [[InlineKeyboardButton("🛒 Į krepšelį", callback_data=f"addcart_{prod_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_photo(photo=photo, caption=caption, reply_markup=reply_markup)


# Tekstinis mygtukas "🛒 Krepšelis"
@check_blacklist
async def text_show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    items = db_execute("""
        SELECT p.id, p.name, p.price
        FROM cart c JOIN products p ON c.product_id=p.id
        WHERE c.user_id=?
        """,
        (user_id,),
        fetch='all',
        db_name=DB_PATH
    )

    if not items:
        await update.message.reply_text("🛒 Tavo krepšelis tuščias.")
        return

    text = "🛒 Tavo krepšelis:\n\n"
    keyboard = []
    total = 0

    for it in items:
        prod_id, name, price = it
        text += f"• {name}: {price} €\n"
        keyboard.append([InlineKeyboardButton(f"🗑️ Pašalinti: {name}", callback_data=f"remove_{prod_id}")])
        total += price

    text += f"\n💰 Suma: {total} €"

    keyboard.append([InlineKeyboardButton("✅ Užsakyti", callback_data="checkout")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup)
