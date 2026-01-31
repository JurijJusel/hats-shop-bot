from telegram import (Update,
                    InlineKeyboardButton,
                    InlineKeyboardMarkup)
from telegram.ext import ContextTypes
import sqlite3
from constants import DB_PATH
import logging

logger = logging.getLogger(__name__)


# Rodyti krepšelį
async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.id, p.name, p.price
            FROM cart c JOIN products p ON c.product_id=p.id
            WHERE c.user_id=?
        """, (user_id,))
        items = cursor.fetchall()

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
        await query.message.reply_text(text, reply_markup=reply_markup)

    except sqlite3.Error as e:
        logger.error(f"Database error in show_cart for user {user_id}: {e}")
        await query.message.reply_text(
            "❌ Įvyko duomenų bazės klaida. Prašome bandyti dar kartą."
        )
    except Exception as e:
        logger.error(f"Unexpected error in show_cart for user {user_id}: {e}", exc_info=True)
        await query.message.reply_text("❌ Įvyko netikėta klaida. Prašome bandyti dar kartą.")
    finally:
        if conn:
            conn.close()


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

    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cart WHERE user_id=? AND product_id=?", (user_id, prod_id))
        conn.commit()

        logger.info(f"User {user_id} removed product {prod_id} from cart")

        await query.message.edit_text("✅ Prekė pašalinta iš krepšelio!")
        # Iškart parodom atnaujintą krepšelį
        await show_cart(update, context)

    except sqlite3.Error as e:
        logger.error(f"Database error in remove_from_cart for user {user_id}, product {prod_id}: {e}")
        await query.message.reply_text(
            "❌ Įvyko duomenų bazės klaida. Prašome bandyti dar kartą."
        )
    except Exception as e:
        logger.error(f"Unexpected error in remove_from_cart for user {user_id}, product {prod_id}: {e}", exc_info=True)
        await query.message.reply_text("❌ Įvyko netikėta klaida. Prašome bandyti dar kartą.")
    finally:
        if conn:
            conn.close()


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

    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Tikrinam ar kepurė dar prieinama
        cursor.execute('SELECT available FROM products WHERE id = ?', (product_id,))
        result = cursor.fetchone()

        if not result or result[0] == 0:
            logger.warning(f"User {user_id} tried to add unavailable product {product_id}")

            await query.edit_message_caption(
                caption="❌ **Ši kepurė jau parduota arba nebeprieinama!**\n\n"
                        "Atsiprašome, kažkas spėjo greičiau. 😔",
                reply_markup=None
            )
            return

        # Tikrinti ar jau yra krepšelyje
        cursor.execute(
            'SELECT * FROM cart WHERE user_id = ? AND product_id = ?',
            (user_id, product_id)
        )

        if cursor.fetchone():
            logger.info(f"User {user_id} tried to add duplicate product {product_id}")

            await query.edit_message_caption(
                caption="⚠️ **Ši kepurė jau yra jūsų krepšelyje!**",
                reply_markup=None
            )
            return

        # Pridėti į krepšelį
        cursor.execute(
            'INSERT INTO cart (user_id, product_id) VALUES (?, ?)',
            (user_id, product_id)
        )
        conn.commit()

        logger.info(f"User {user_id} added product {product_id} to cart")

        await query.edit_message_caption(
            caption="✅ **Kepurė pridėta į krepšelį!**\n\n"
                    "Spauskite 🛒 **Krepšelis** meniu apačioje.",
            reply_markup=None
        )

    except sqlite3.Error as e:
        logger.error(f"Database error in add_to_cart for user {user_id}, product {product_id}: {e}")
        await query.edit_message_caption(
            caption="❌ **Įvyko duomenų bazės klaida. Prašome bandyti dar kartą.**",
            reply_markup=None
        )
    except Exception as e:
        logger.error(f"Unexpected error in add_to_cart for user {user_id}, product {product_id}: {e}", exc_info=True)
        await query.edit_message_caption(
            caption="❌ **Įvyko netikėta klaida. Prašome bandyti dar kartą.**",
            reply_markup=None
        )
    finally:
        if conn:
            conn.close()
