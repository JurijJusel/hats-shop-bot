import sqlite3
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from config import DB_PATH, ADMINS, SHOW_ORDERS_COUNTS


async def show_orders_base(update: Update, context: ContextTypes.DEFAULT_TYPE, limit: int = None, only_pending: bool = False):
    user_id = update.message.from_user.id
    if user_id not in ADMINS:
        await update.message.reply_text("❌ Neturi teisės peržiūrėti užsakymų.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if only_pending:
        # TIK neužbaigti užsakymai
        sql = """
            SELECT id, user_name, phone, email, city, info, total_price, status
            FROM orders
            WHERE status IN ('naujas', 'apmoketa', 'laukia apmokejimo', 'laukia patvirtinimo')
            ORDER BY id DESC
        """
    else:
        # VISI užsakymai
        sql = """
            SELECT id, user_name, phone, email, city, info, total_price, status
            FROM orders
            ORDER BY id DESC
        """

    # Pridėti LIMIT jei reikia
    if limit:
        sql += " LIMIT ?"
        cursor.execute(sql, (limit,))
    else:
        cursor.execute(sql)

    orders = cursor.fetchall()

    if not orders:
        msg = "📭 Nėra laukiančių užsakymų." if only_pending else "📭 Užsakymų nėra."
        await update.message.reply_text(msg)
        conn.close()
        return

    for order in orders:
        order_id, user_name, phone, email, city, info, total, status = order

        # Gaunam prekes iš order_items
        cursor.execute("""
            SELECT product_name, price_per_unit
            FROM order_items
            WHERE order_id=?
        """, (order_id,))
        items = cursor.fetchall()

        # Suformuojam prekių tekstą
        items_text = ""
        if items:
            items_text = "\n📦 Prekės:\n"
            for product_name, price in items:
                items_text += f"  • {product_name} - {price} €\n"

        admin_text = f"🆕 Užsakymas #{order_id}\n\n" \
                     f"Statusas: {status}\n\n" \
                     f"👤 {user_name}\n📞 {phone}\n📧 {email}\n🏙 {city}\n📝 {info}" \
                     f"{items_text}" \
                     f"💰 Suma: {total} €"

        # Mygtukų logika pagal statusą
        keyboard_admin = []
        if status in ["naujas", "laukia apmokėjimo", "laukia patvirtinimo"]:
            keyboard_admin.append([InlineKeyboardButton("✅ APMOKĖTA", callback_data=f"admin_paid_{order_id}"),
                                   InlineKeyboardButton("📦 IŠSIŲSTA", callback_data=f"admin_shipped_{order_id}")])
        elif status == "apmoketa":
            keyboard_admin.append([InlineKeyboardButton("📦 IŠSIŲSTA", callback_data=f"admin_shipped_{order_id}")])
        reply_markup = InlineKeyboardMarkup(keyboard_admin) if keyboard_admin else None

        await update.message.reply_text(text=admin_text, reply_markup=reply_markup)

    conn.close()


# ADMIN visi užsakymai
async def admin_show_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_orders_base(update, context, limit=None, only_pending=False)

# ADMIN 10 naujausių užsakymų nuruodoma count iš config.py
async def admin_show_orders_10(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_orders_base(update, context, limit=SHOW_ORDERS_COUNTS, only_pending=False)

# ADMIN neužbaigti užsakymai
async def admin_show_orders_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_orders_base(update, context, limit=None, only_pending=True)
