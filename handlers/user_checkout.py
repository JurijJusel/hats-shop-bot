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
import sqlite3
from config import ADMINS, DB_PATH


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

# Checkout (name)
#async def checkout_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#    query = update.callback_query
#    await query.answer()
#    await query.message.reply_text("Įveskite savo VARDA:")
#    return NAME

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

## Checkout (phone)
#async def checkout_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
#    name = update.message.text

#    if len(name) >= 30:
#        await update.message.reply_text(
#            "❌ Vardas per ilgas! Maksimalus ilgis - 30 simbolių.\n"
#            "Įveskite trumpesnį VARDĄ:"
#        )
#        return NAME
#    context.user_data['name'] = update.message.text
#    await update.message.reply_text("Įveskite savo TELEFONO numerį:")
#    return PHONE

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

## Checkout (email)
#async def checkout_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
#    phone = update.message.text

#    if len(phone) >= 15:
#        await update.message.reply_text(
#            "❌ Telefono numeris per ilgas arba neteisingas!\n"
#            "Maksimalus ilgis - 15 simbolių."
#        )
#        return PHONE
#    context.user_data['phone'] = update.message.text
#    await update.message.reply_text("Įveskite savo EL. PAŠTĄ:")
#    return EMAIL

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

## Checkout (city)
#async def checkout_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
#    email = update.message.text

#    if len(email) >= 40:
#        await update.message.reply_text(
#            "❌ El. paštas per ilgas! Maksimalus ilgis - 40 simbolių.\n"
#            "Įveskite trumpesnį EL. PAŠTĄ:"
#        )
#        return EMAIL
#    context.user_data['email'] = update.message.text
#    await update.message.reply_text("Įveskite savo MIESTĄ:")
#    return CITY

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

## Checkout (info) + add order to DB
#async def checkout_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
#    city = update.message.text

#    if len(city) >= 30:
#        await update.message.reply_text(
#            "❌ Miesto pavadinimas per ilgas! Maksimalus ilgis - 30 simbolių.\n"
#            "Įveskite trumpesnį MIESTĄ:"
#        )
#        return CITY
#    context.user_data['city'] = update.message.text
#    await update.message.reply_text(
#        f"Papildoma informacija.\n"
#        f"Cia galima parasyti pastabas dėl pristatymo.\n"
#        f"arba tikslu vienipak adresa is kur jus pasiimsite siunta \n"
#        f"tai pagreitins uzsakymo apdorojima ir greita issiuntima.\n"
#        f"Jei nėra – parašykite ,-' ."
#        )
#    return INFO

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

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
                SELECT p.id, p.name, p.price, p.photo_file_id
                FROM cart c
                JOIN products p ON c.product_id = p.id
                WHERE c.user_id = ?""",
                    (user_id,))
    items = cursor.fetchall()
    if not items:
        await update.message.reply_text("Krepšelis tuščias 😢")
        conn.close()
        return ConversationHandler.END

    # Sukuriame order
    cursor.execute("""INSERT INTO orders
                   (user_id, user_name, phone, email, info, city)
                   VALUES (?,?,?,?,?,?)""",
                   (user_id,
                    context.user_data['name'],
                    context.user_data['phone'],
                    context.user_data['email'],
                    context.user_data['info'],
                    context.user_data['city']))

    order_id = cursor.lastrowid

    total = 0
    products_text = ""
    media = []

    for it in items:
        prod_id, name, price, photo_id = it

        cursor.execute("""
            INSERT INTO order_items
            (order_id, product_id, product_name, price_per_unit, photo_file_id)
            VALUES (?,?,?,?,?)
        """, (order_id, prod_id, name, price, photo_id))

        cursor.execute("UPDATE products SET available=0 WHERE id=?", (prod_id,))

        total += price
        products_text += f" – {name}: {price} €\n"
        if photo_id:
            media.append(InputMediaPhoto(media=photo_id, caption=name))

    # Išvalom cart
    cursor.execute("DELETE FROM cart WHERE user_id=?", (user_id,))
    # Atnaujinam total_price
    cursor.execute("UPDATE orders SET total_price=? WHERE id=?", (total, order_id))
    conn.commit()
    conn.close()

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
    await update.message.reply_text("❌ Užsakymas atšauktas.")
    return ConversationHandler.END

# Order cancel handler (BUTTON version)
async def order_cancel_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.edit_text("❌ Užsakymas atšauktas.")
    return ConversationHandler.END

#async def order_cancel_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
#    query = update.callback_query
#    await query.answer()
#    await query.message.edit_text("❌ Užsakymas atšauktas.")
#    return ConversationHandler.END

# Payment confirmed handler (USER spaudžia "APMOKĖTA")
async def payment_confirmed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    order_id = int(query.data.split("_")[1])

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status='laukia patvirtinimo' WHERE id=?", (order_id,))
    conn.commit()
    conn.close()

    # Žinutė vartotojui
    await query.message.edit_text(
        f"✅ Užsakymas #{order_id} pažymėtas kaip APMOKĖTAS.\n"
        f"Laukiama Admino patvirtinimo.\n\n"
        f"📋 Stebėkite būseną ivedus komanda: /my_orders"
    )

    # Žinutė adminui
    admin_msg = f"💰 Užsakymas #{order_id} pažymėtas kaip APMOKĖTAS.\nVartotojas laukia patvirtinimo."
    for admin_id in ADMINS:
        await context.bot.send_message(chat_id=admin_id, text=admin_msg)

## Checkout ConversationHandler
#conversation_handler = ConversationHandler(
#    entry_points=[CallbackQueryHandler(checkout_start, pattern="checkout")],
#    states={
#        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, checkout_name)],
#        PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, checkout_phone)],
#        EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, checkout_email)],
#        CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, checkout_city)],
#        INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, checkout_info)],
#    },
#    fallbacks=[CommandHandler("cancel", order_cancel)],
#)

conversation_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(checkout_start, pattern="checkout")],
    states={
        NAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, checkout_name),
            CallbackQueryHandler(order_cancel_button, pattern="cancel_order")  # PRIDĖTI!
        ],
        PHONE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, checkout_phone),
            CallbackQueryHandler(order_cancel_button, pattern="cancel_order")  # PRIDĖTI!
        ],
        EMAIL: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, checkout_email),
            CallbackQueryHandler(order_cancel_button, pattern="cancel_order")  # PRIDĖTI!
        ],
        CITY: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, checkout_city),
            CallbackQueryHandler(order_cancel_button, pattern="cancel_order")  # PRIDĖTI!
        ],
        INFO: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, checkout_info),
            CallbackQueryHandler(order_cancel_button, pattern="cancel_order")  # PRIDĖTI!
        ],
    },
    fallbacks=[
        CommandHandler("cancel", order_cancel)  # /cancel komandai
    ],
)
