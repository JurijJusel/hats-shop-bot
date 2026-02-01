from telegram import (Update,
                    InlineKeyboardButton,
                    InlineKeyboardMarkup)
from telegram.ext import ContextTypes
from constants import DB_PATH
import logging
from database.db_helper import db_execute

logger = logging.getLogger(__name__)


# Rodyti krepšelį
async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    items = db_execute(
        """
        SELECT p.id, p.name, p.price
        FROM cart c JOIN products p ON c.product_id=p.id
        WHERE c.user_id=?
        """,
        (user_id,),
        fetch='all',
        db_name=DB_PATH
        )

    if not items:
        await query.message.reply_text("🛒 Tavo krepšelis tuščias.")
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

    try:
        await query.message.reply_text(text, reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Error sending cart message to user {user_id}: {e}")
        await query.message.reply_text("❌ Įvyko klaida rodant krepšelį. Bandykite dar kartą.")


# Pašalinti vieną prekę iš krepšelio
async def remove_from_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    try:
        prod_id = int(query.data.split("_")[1])
    except (ValueError, IndexError) as e:
        logger.error(f"Error parsing product_id from callback_data: {query.data}, error: {e}")
        await query.message.reply_text("❌ Klaida: Nepavyko nustatyti prekės ID.")
        return

    # Pašalinti iš krepšelio
    success = db_execute(
        "DELETE FROM cart WHERE user_id=? AND product_id=?",
        (user_id, prod_id),
        db_name=DB_PATH
    )

    if success:
        logger.info(f"User {user_id} removed product {prod_id} from cart")
        await query.message.edit_text("✅ Prekė pašalinta iš krepšelio!")
        # Iškart parodom atnaujintą krepšelį
        await show_cart(update, context)
    else:
        logger.error(f"Failed to remove product {prod_id} from cart for user {user_id}")
        await query.message.reply_text("❌ Klaida šalinant prekę. Bandykite dar kartą.")


# Pridėti į krepšelį
async def add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pridėti kepurę į krepšelį (su tikrinimu ar dar prieinama)"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id

    try:
        product_id = int(query.data.split('_')[1])
    except (ValueError, IndexError) as e:
        logger.error(f"Error parsing product_id from callback_data: {query.data}, error: {e}")
        await query.edit_message_caption(
            caption="❌ **Klaida: Nepavyko nustatyti prekės ID.**",
            reply_markup=None
        )
        return

    # Tikrinam ar kepurė dar prieinama
    result = db_execute(
        'SELECT available FROM products WHERE id = ?',
        (product_id,),
        fetch='one',
        db_name=DB_PATH
    )

    if not result or result[0] == 0:
        logger.warning(f"User {user_id} tried to add unavailable product {product_id}")

        await query.edit_message_caption(
            caption="❌ **Ši kepurė jau parduota arba nebeprieinama!**\n\n"
                    "Atsiprašome, kažkas spėjo greičiau. 😔",
            reply_markup=None
        )
        return

    # Tikrinti ar jau yra krepšelyje
    success = db_execute(
        'SELECT * FROM cart WHERE user_id = ? AND product_id = ?',
        (user_id, product_id),
        fetch='one',
        db_name=DB_PATH
    )

    if success:
        logger.info(f"User {user_id} tried to add duplicate product {product_id}")

        await query.edit_message_caption(
            caption="⚠️ **Ši kepurė jau yra jūsų krepšelyje!**",
            reply_markup=None
        )
        return

    # Pridėti į krepšelį
    success = db_execute(
        'INSERT INTO cart (user_id, product_id) VALUES (?, ?)',
        (user_id, product_id),
        db_name=DB_PATH
    )

    if success:
        logger.info(f"User {user_id} added product {product_id} to cart")
        await query.edit_message_caption(
            caption="✅ **Kepurė pridėta į krepšelį!**\n\n"
                    "Spauskite 🛒 **Krepšelis** meniu apačioje.",
            reply_markup=None
        )
    else:
        logger.error(f"Failed to add product {product_id} to cart for user {user_id}")
        await query.edit_message_caption(
            caption="❌ **Įvyko klaida pridedant į krepšelį. Bandykite dar kartą.**",
            reply_markup=None
        )
