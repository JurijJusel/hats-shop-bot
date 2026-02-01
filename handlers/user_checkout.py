from telegram import (Update,
                    InlineKeyboardButton,
                    InlineKeyboardMarkup,
                    InputMediaPhoto)
from telegram.ext import (CommandHandler,
                        CallbackQueryHandler,
                        MessageHandler,
                        ContextTypes,
                        filters,
                        ConversationHandler)
from constants import ADMINS, DB_PATH
import logging
from database.db_helper import db_execute

logger = logging.getLogger(__name__)

# States for checkout
NAME, PHONE, EMAIL, CITY, INFO = range(5)


# Checkout (name) - SU MYGTUKU
async def checkout_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [[InlineKeyboardButton("❌ Atšaukti", callback_data="order_cancel_")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.reply_text(
        "Įveskite savo VARDĄ:",
        reply_markup=reply_markup
    )
    return NAME


# Checkout (phone) - SU MYGTUKU
async def checkout_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text

    if len(name) >= 30:
        await update.message.reply_text(
            "❌ Vardas per ilgas! Maksimalus ilgis - 30 simbolių.\n"
            "Įveskite trumpesnį VARDĄ:"
        )
        return NAME

    context.user_data['name'] = update.message.text

    keyboard = [[InlineKeyboardButton("❌ Atšaukti", callback_data="cancel_order")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Įveskite savo TELEFONO numerį:",
        reply_markup=reply_markup
    )
    return PHONE


# Checkout (email) - SU MYGTUKU
async def checkout_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text

    if len(phone) >= 15:
        await update.message.reply_text(
            "❌ Telefono numeris per ilgas arba neteisingas!\n"
            "Maksimalus ilgis - 15 simbolių."
        )
        return PHONE

    context.user_data['phone'] = update.message.text

    keyboard = [[InlineKeyboardButton("❌ Atšaukti", callback_data="cancel_order")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Įveskite savo EL. PAŠTĄ:",
        reply_markup=reply_markup
    )
    return EMAIL


# Checkout (city) - SU MYGTUKU
async def checkout_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text

    if len(email) >= 40:
        await update.message.reply_text(
            "❌ El. paštas per ilgas! Maksimalus ilgis - 40 simbolių.\n"
            "Įveskite trumpesnį EL. PAŠTĄ:"
        )
        return EMAIL

    context.user_data['email'] = update.message.text

    keyboard = [[InlineKeyboardButton("❌ Atšaukti", callback_data="cancel_order")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Įveskite savo MIESTĄ:",
        reply_markup=reply_markup
    )
    return CITY


# Checkout (info) - SU MYGTUKU
async def checkout_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = update.message.text

    if len(city) >= 30:
        await update.message.reply_text(
            "❌ Miesto pavadinimas per ilgas! Maksimalus ilgis - 30 simbolių.\n"
            "Įveskite trumpesnį MIESTĄ:"
        )
        return CITY

    context.user_data['city'] = update.message.text

    keyboard = [[InlineKeyboardButton("❌ Atšaukti", callback_data="cancel_order")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"Papildoma informacija.\n"
        f"Cia galima parasyti pastabas dėl pristatymo.\n"
        f"arba tikslu vienipak adresa is kur jus pasiimsite siunta \n"
        f"tai pagreitins uzsakymo apdorojima ir greita issiuntima.\n"
        f"Jei nėra – parašykite ,-' .",
        reply_markup=reply_markup
    )
    return INFO


# Checkout (info) + add order to DB
async def checkout_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    info = update.message.text
    if len(info) >= 500:
        await update.message.reply_text(
            "❌ Papildoma informacija per ilga! Maksimalus ilgis - 500 simbolių.\n"
            "Įveskite trumpesnę PAPILDOMĄ INFORMACIJĄ:"
        )
        return INFO

    context.user_data['info'] = update.message.text
    user_id = update.message.from_user.id

    #conn = sqlite3.connect(DB_PATH)
    #cursor = conn.cursor()

    items = db_execute(
        """
        SELECT p.id, p.name, p.price, p.photo_file_id
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = ?
        """,
        (user_id,),
        fetch='all',
        db_name=DB_PATH
    )

    if not items:
        logger.info(f"User {user_id} checkout failed - empty cart")
        await update.message.reply_text("Krepšelis tuščias 😢")

        return ConversationHandler.END

    # Sukuriame order
    order_id = db_execute(
        """
        INSERT INTO orders
        (user_id, user_name, phone, email, info, city)
        VALUES (?,?,?,?,?,?)
        """,
        (user_id,
        context.user_data['name'],
        context.user_data['phone'],
        context.user_data['email'],
        context.user_data['info'],
        context.user_data['city']),
        fetch='lastrowid',
        db_name=DB_PATH,
        )

    if not order_id:
        logger.error(f"Failed to create order for user {user_id}")
        await update.message.reply_text("❌ Įvyko klaida kuriant užsakymą. Bandykite dar kartą.")
        return ConversationHandler.END

    total = 0
    products_text = ""
    media = []

    for prod_id, name, price, photo_id in items:
        db_execute(
            """
            INSERT INTO order_items
            (order_id, product_id, product_name, price_per_unit, photo_file_id)
            VALUES (?,?,?,?,?)
            """,
            (order_id, prod_id, name, price, photo_id),
            db_name=DB_PATH
        )

        # Pažymime produktą kaip nepasiekiamą
        db_execute(
            "UPDATE products SET available=0 WHERE id=?",
            (prod_id,),
            db_name=DB_PATH
        )

        total += price
        products_text += f" – {name}: {price} €\n"
        if photo_id:
            media.append(InputMediaPhoto(media=photo_id, caption=name))

    # Išvalom cart
    db_execute(
        "DELETE FROM cart WHERE user_id=?",
        (user_id,),
        db_name=DB_PATH
    )

    # Atnaujinam total_price
    db_execute(
        "UPDATE orders SET total_price=? WHERE id=?",
        (total, order_id),
        db_name=DB_PATH
    )

    logger.info(f"Order #{order_id} created: user={user_id}, total={total}€, items={len(items)}")

    # Žinutė vartotojui
    keyboard_user = [
        [InlineKeyboardButton("💳 APMOKĖTA", callback_data=f"paid_{order_id}")]
    ]

    await update.message.reply_text(
        f"🎉 Užsakymas patvirtintas!\n"
        f"💰 Suma: {total} €\n"
        f"📦 Mes susisieksime su jumis dėl pristatymo jei kils neaiškumu.\n\n"
        f"Banko saskaita apmokejimui: LT123456789012345678\n\n"
        f"Galima Revolut Nr. +37068130478\n\n"
        f"Paspauskite mygtuką APMOKĖTA žemiau, kai būsite apmokėję:",
        reply_markup=InlineKeyboardMarkup(keyboard_user)
    )

    # Žinutė adminui
    admin_msg = (
        f"🆕 Naujas užsakymas #{order_id}\n\n"
        f"Statusas: LAUKIAMA apmokėjimo\n\n"
        f"👤 {context.user_data['name']}\n"
        f"📞 {context.user_data['phone']}\n"
        f"📧 {context.user_data['email']}\n"
        f"🏙 {context.user_data['city']}\n"
        f"📝 {context.user_data['info']}\n\n"
        f"📦 Užsakytos prekės:\n"
        f"{products_text}"
        f"\n💰 Suma: {total} €"
    )

    keyboard_admin = [
        [
        InlineKeyboardButton("✅ APMOKĖTA", callback_data=f"admin_paid_{order_id}"),
        InlineKeyboardButton("📦 IŠSIŲSTA", callback_data=f"admin_shipped_{order_id}")
        ]
    ]

    for admin_id in ADMINS:
        # Siunčiam media grupę su prekėmis
        if media:
            await context.bot.send_media_group(chat_id=admin_id, media=media)
        # Siunčiam tekstinę žinutę su statusu ir mygtukais
        await context.bot.send_message(chat_id=admin_id,
                                       text=admin_msg,
                                       reply_markup=InlineKeyboardMarkup(keyboard_admin))

    return ConversationHandler.END

# Order cancel handler
async def order_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Order cancel via /cancel command by user {update.message.from_user.id}")
    await update.message.reply_text("❌ Užsakymas atšauktas.")
    return ConversationHandler.END

# Order cancel handler (BUTTON version)
async def order_cancel_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    logger.info(f"Order cancelled via BUTTON by user {query.from_user.id}")
    await query.answer()
    await query.message.edit_text("❌ Užsakymas atšauktas.")
    return ConversationHandler.END

# Payment confirmed handler (USER spaudžia "APMOKĖTA")
async def payment_confirmed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        order_id = int(query.data.split("_")[1])
    except (ValueError, IndexError) as e:
        logger.error(f"Error parsing order_id from callback_data: {query.data}, error: {e}")
        await query.message.reply_text("❌ Klaida: Nepavyko nustatyti užsakymo ID.")
        return

    logger.info(f"Order #{order_id} marked as PAID by user {query.from_user.id}")

    success = db_execute(
        "UPDATE orders SET status='laukia patvirtinimo' WHERE id=?",
        (order_id,),
        db_name=DB_PATH
    )

    if not success:
        logger.error(f"Database error in payment_confirmed for order #{order_id}")
        await query.message.reply_text(
            "❌ Įvyko duomenų bazės klaida. Prašome bandyti dar kartą."
        )
        return

    # Žinutė vartotojui
    try:
        await query.message.edit_text(
            f"✅ Užsakymas #{order_id} pažymėtas kaip APMOKĖTAS.\n"
            f"Laukiama Admino patvirtinimo.\n\n"
            f"📋 Stebėkite būseną ivedus komanda: /my_orders"
        )
    except Exception as e:
        logger.error(f"Error editing message for user {query.from_user.id}: {e}")

    # Žinutė adminui
    admin_msg = f"💰 Užsakymas #{order_id} pažymėtas kaip APMOKĖTAS.\nVartotojas laukia patvirtinimo."
    for admin_id in ADMINS:
        try:
            await context.bot.send_message(chat_id=admin_id, text=admin_msg)
        except Exception as e:
            logger.error(f"Error sending message to admin {admin_id}: {e}")


conversation_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(checkout_start, pattern="checkout")],
    states={
        NAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, checkout_name),
            CallbackQueryHandler(order_cancel_button, pattern="cancel_order")
        ],
        PHONE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, checkout_phone),
            CallbackQueryHandler(order_cancel_button, pattern="cancel_order")
        ],
        EMAIL: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, checkout_email),
            CallbackQueryHandler(order_cancel_button, pattern="cancel_order")
        ],
        CITY: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, checkout_city),
            CallbackQueryHandler(order_cancel_button, pattern="cancel_order")
        ],
        INFO: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, checkout_info),
            CallbackQueryHandler(order_cancel_button, pattern="cancel_order")
        ],
    },
    fallbacks=[
        CommandHandler("cancel", order_cancel)  # /cancel komandai
    ],
)
