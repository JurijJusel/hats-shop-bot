from telegram import (Update,
                    InlineKeyboardButton,
                    InlineKeyboardMarkup)
from telegram.ext import ContextTypes
import sqlite3
from constants import DB_PATH


# Rodyti krepšelį
async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.id, p.name, p.price
        FROM cart c JOIN products p ON c.product_id=p.id
        WHERE c.user_id=?
    """, (user_id,))
    items = cursor.fetchall()
    conn.close()

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


# Pašalinti vieną prekę iš krepšelio
async def remove_from_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    prod_id = int(query.data.split("_")[1])

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cart WHERE user_id=? AND product_id=?", (user_id, prod_id))
    conn.commit()
    conn.close()

    await query.message.edit_text("✅ Prekė pašalinta iš krepšelio!")
    # Iškart parodom atnaujintą krepšelį
    await show_cart(update, context)


# Pridėti į krepšelį
async def add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pridėti kepurę į krepšelį (su tikrinimu ar dar prieinama)"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    product_id = int(query.data.split('_')[1])

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Tikrinam ar kepurė dar prieinama
    cursor.execute('SELECT available FROM products WHERE id = ?', (product_id,))
    result = cursor.fetchone()

    if not result or result[0] == 0:
        conn.close()
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
        conn.close()
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
    conn.close()

    await query.edit_message_caption(
        caption="✅ **Kepurė pridėta į krepšelį!**\n\n"
                "Spauskite 🛒 **Krepšelis** meniu apačioje.",
        reply_markup=None
    )
