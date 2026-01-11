from telegram import Update, InputMediaPhoto
from telegram.ext import ContextTypes
import sqlite3
from config import DB_PATH


async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Paimam visus vartotojo užsakymus
    cursor.execute("""
        SELECT id, order_date, status, total_price, tracking_number
        FROM orders
        WHERE user_id=?
        ORDER BY id DESC
    """, (user_id,))
    orders = cursor.fetchall()

    if not orders:
        await update.message.reply_text("📭 Jūs dar neturite užsakymų.")
        conn.close()
        return

    for order_id, order_date, status, total, tracking_number in orders:
        # Gaunam prekes
        cursor.execute("""
            SELECT product_name, price_per_unit, photo_file_id
            FROM order_items
            WHERE order_id=?
        """, (order_id,))
        items = cursor.fetchall()

        # Status emoji
        if status == "naujas" or status == "laukia patvirtinimo":
            status_emoji = "⏳"
        elif status == "apmoketa":
            status_emoji = "✅"
        elif status == "issiusta":
            status_emoji = "📦"
        else:
            status_emoji = "📋"

        # Tekstas
        text = f"{status_emoji} *Užsakymas #{order_id}*\n\n"
        text += f"📊 Statusas: {status}\n"
        text += f"📦 Tracking: {tracking_number or '—'}\n"
        text += f"📅 {order_date[:10]}\n\n"
        text += f"💰 Suma: {total}€\n\n"
        text += f"🛍 Prekės:\n"

        # Prekės su nuotraukomis (LIMIT 5)
        photos = []
        for product_name, price, photo_id in items:
            text += f"  • {product_name} - {price}€\n"
            if photo_id and len(photos) < 5:  # ← LIMITAS 5
                photos.append(photo_id)

        # Jei daugiau nei 5 prekės, parodom pastabą
        if len(items) > 5:
            text += f"\n_...ir dar {len(items) - 5} prekė(-s)_"

        # Siųsti su nuotraukomis
        if photos:
            # Jei yra 1 nuotrauka - siųsti kaip photo su caption
            if len(photos) == 1:
                await update.message.reply_photo(
                    photo=photos[0],
                    caption=text,
                    parse_mode="Markdown"
                )
            # Jei daugiau - siųsti kaip media group
            else:
                media = [InputMediaPhoto(media=photos[0], caption=text, parse_mode="Markdown")]
                for photo in photos[1:]:
                    media.append(InputMediaPhoto(media=photo))
                await update.message.reply_media_group(media=media)
        else:
            # Jei nėra nuotraukų - siųsti tik tekstą
            await update.message.reply_text(text, parse_mode="Markdown")

    conn.close()
