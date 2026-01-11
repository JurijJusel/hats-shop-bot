from telegram import Update
from telegram.ext import ContextTypes
import sqlite3
from config import DB_PATH


# ADMIN patvirtina apmokėjimą
async def admin_paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    order_id = int(query.data.split("_")[2])  # admin_paid_123 -> 123

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status='apmoketa' WHERE id=?", (order_id,))

    # Gauname user_id
    cursor.execute("SELECT user_id FROM orders WHERE id=?", (order_id,))
    result = cursor.fetchone()
    conn.commit()
    conn.close()

    if result:
        user_id = result[0]
        # Pranešimas user'iui
        await context.bot.send_message(
            chat_id=user_id,
            text = f"✅ Jūsų užsakymas #{order_id} patvirtintas kaip APMOKĖTAS!\n\n"
                    f"📋 Stebėkite būseną bet kada ivedus komanda: /my_orders"
        )

    # Atnaujinti admin žinutę - PALIEKAME TIK IŠSIŲSTA mygtuką
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup

    keyboard = [[InlineKeyboardButton("📦 IŠSIŲSTA", callback_data=f"admin_shipped_{order_id}")]]

    await query.message.edit_text(
        query.message.text, #+ f"\n\n✅ Apmokėjimas patvirtintas!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ADMIN pažymi kaip išsiųsta
async def admin_shipped(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    order_id = int(query.data.split("_")[2])  # admin_shipped_123 -> 123

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status='issiusta' WHERE id=?", (order_id,))

    # Gauname user_id
    cursor.execute("SELECT user_id FROM orders WHERE id=?", (order_id,))
    result = cursor.fetchone()
    conn.commit()
    conn.close()

    if result:
        user_id = result[0]
        # Pranešimas user'iui
        await context.bot.send_message(
            chat_id=user_id,
            text = f"📦 Jūsų užsakymas #{order_id} IŠSIŲSTAS! 🚚\n"
                    f"Ačiū kad pirkote!\n\n"
                    f"📋 Peržiūrėti užsakymus: /my_orders"
        )

    # Atnaujinti admin žinutę - PAŠALINAME VISUS MYGTUKUS
    await query.message.edit_text(
        query.message.text #+ f"\n\n📦 Užsakymas išsiųstas!"
    )
