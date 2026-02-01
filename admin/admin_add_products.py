from telegram.ext import (CommandHandler,
                          ContextTypes,
                          MessageHandler,
                          ConversationHandler,
                          filters)
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from constants import ADMINS, DB_PATH
import logging
from database.db_helper import db_execute

logger = logging.getLogger(__name__)


PHOTO, NAME, DESCRIPTION, PRICE = range(4)


async def add_product_start(update, context):
    if update.message.from_user.id not in ADMINS:

        logger.info(f"Unauthorized /add_hat attempt by user {update.message.from_user.id}")

        await update.message.reply_text("❌ Tik admin gali pridėti prekes.")
        return ConversationHandler.END
    await update.message.reply_text("Siųskite 🧢 kepurės nuotrauką (kaip foto):")
    return PHOTO


async def add_product_photo(update, context):
    # Tikriname, ar tikrai gauta foto
    if not update.message.photo:
        await update.message.reply_text("❌ Prašome siųsti nuotrauką kaip foto, ne failą.")
        return PHOTO

    # Paimame didžiausios kokybės foto ID
    file_id = update.message.photo[-1].file_id
    context.user_data['photo_file_id'] = file_id

    await update.message.reply_text("🧢 Įveskite kepurės pavadinimą:")
    return NAME


async def add_product_name(update, context):
    name = update.message.text
    if len(name) >= 40:
        await update.message.reply_text(
            "❌ Pavadinimas per ilgas! Maksimalus ilgis - 40 simbolių.\n"
            "Įveskite trumpesnį PAVADINIMĄ:"
        )
        return NAME
    context.user_data['name'] = update.message.text
    await update.message.reply_text("📝 Įveskite aprašymą:")
    return DESCRIPTION


async def add_product_description(update, context):
    description = update.message.text
    if len(description) >= 1000:
        await update.message.reply_text(
            "❌ Aprašymas per ilgas! Maksimalus ilgis - 1000 simbolių.\n"
            "Įveskite trumpesnį APRAŠYMĄ:"
        )
        return DESCRIPTION
    context.user_data['description'] = update.message.text
    await update.message.reply_text("💰 Įveskite kainą (pvz., 15.0):")
    return PRICE


async def add_product_price(update, context):
    try:
        price = int(update.message.text)
    except ValueError:
        await update.message.reply_text("❌ Įveskite teisingą sveiką skaičių kainai (pvz.,25).")
        return PRICE
    context.user_data['price'] = price

    success = db_execute(
        """
        INSERT INTO products(name, description, price, photo_file_id)
        VALUES (?, ?, ?, ?)
        """,
        (
            context.user_data['name'],
            context.user_data['description'],
            context.user_data['price'],
            context.user_data['photo_file_id']
        ),
        db_name=DB_PATH
    )

    if success:
        logger.info(f"Admin {update.message.from_user.id} added product: '{context.user_data['name']}', price: ({price}€)")
        await update.message.reply_text(f"✅ Kepurė '{context.user_data['name']}' sėkmingai pridėta!")
    else:
        await update.message.reply_text("❌ Klaida pridedant kepurę!")
        logger.error(f"Failed to add product: {context.user_data.get('name')}")

    return ConversationHandler.END


async def add_product_cancel(update, context):
    await update.message.reply_text("❌ Pridėjimas atšauktas.")
    return ConversationHandler.END


async def admin_show_products(update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in ADMINS:
        await update.message.reply_text("❌ Tik admin gali matyti produktų sąrašą.")
        return

    #conn = sqlite3.connect(DB_PATH)
    #cursor = conn.cursor()
    products = db_execute(
        """
        SELECT id, name, description, price, photo_file_id, category, available, created_date
        FROM products
        """,
        fetch='all',
        db_name=DB_PATH
    )

    if not products:
        await update.message.reply_text("❌ Šiuo metu produktų nėra.")
        return

    for product in products:
        id, name, description, price, photo_file_id, category, available, created_date = product
        available_text = "✅ Yra" if available else "❌ Nėra"
        text = (
            f"🆔 ID: {id}\n"
            f"📦 Pavadinimas: {name}\n"
            f"📝 Aprašymas: {description}\n"
            f"💰 Kaina: {price} €\n"
            f"📂 Kategorija: {category}\n"
            f"📌 Prieinamumas: {available_text}\n"
            f"📅 Sukurta: {created_date}"
        )

        # Sąlyginis mygtukas pagal prieinamumą
        if available == 1:
            # Jei yra sandėlyje - rodyti "Ištrinti"
            keyboard = [[InlineKeyboardButton(f"🗑️ Ištrinti (ID: {id})", callback_data=f"delete_hat_{id}")]]
        else:
            # Jei nėra sandėlyje - rodyti "Aktyvuoti"
            keyboard = [[InlineKeyboardButton(f"✅ Aktyvuoti (ID: {id})", callback_data=f"activate_hat_{id}")]]

        reply_markup = InlineKeyboardMarkup(keyboard)

        if photo_file_id:
            await update.message.reply_photo(photo=photo_file_id, caption=text, reply_markup=reply_markup)
        else:
            await update.message.reply_text(text, reply_markup=reply_markup)


async def delete_hat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Tikrinam admin teises
    if query.from_user.id not in ADMINS:
        await query.message.reply_text("❌ Tik admin gali ištrinti kepures.")
        return

    # Gauname ID iš callback_data
    hat_id = int(query.data.split("_")[2])

    # Tikrinam ar kepurė egzistuoja
    product = db_execute(
        "SELECT name FROM products WHERE id=?",
        (hat_id,),
        fetch='one',
        db_name=DB_PATH
    )

    if not product:
        await query.message.reply_text("❌ Kepurė nerasta.")
        return

    product_name = product[0]

    # Ištriname kepurę
    del_success = db_execute(
        "DELETE FROM products WHERE id=?",
        (hat_id,),
        db_name=DB_PATH
    )

    if del_success:
        logger.info(f"Admin {query.from_user.id} deleted product: '{product_name}' (ID: {hat_id})")
        # Ištriname seną žinutę ir siunčiame naują
        await query.message.delete()
        await query.message.reply_text(f"✅ Kepurė '{product_name}' (ID: {hat_id}) sėkmingai ištrinta!")
    else:
        logger.error(f"Failed to delete product: '{product_name}' (ID: {hat_id}) by admin {query.from_user.id}")
        await query.message.reply_text(f"❌ Klaida trinant kepurę '{product_name}'!")


async def activate_hat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Tikrinam admin teises
    if query.from_user.id not in ADMINS:
        await query.message.reply_text("❌ Tik admin gali aktyvuoti kepures.")
        return

    # Gauname ID iš callback_data
    hat_id = int(query.data.split("_")[2])

    # Tikrinam ar kepurė egzistuoja
    product = db_execute(
        "SELECT name, available FROM products WHERE id=?",
        (hat_id,),
        fetch='one',
        db_name=DB_PATH
    )

    if not product:
        await query.message.reply_text("❌ Kepurė nerasta.")
        return

    product_name, available = product

    if available == 1:
        await query.message.reply_text("⚠️ Ši kepurė jau aktyvi!")
        return

    # Aktyvuojame kepurę
    hat_active_success = db_execute(
        "UPDATE products SET available=1 WHERE id=?",
        (hat_id,),
        db_name=DB_PATH
    )

    if hat_active_success:
        logger.info(f"Admin {query.from_user.id} activated product: '{product_name}' (ID: {hat_id})")
        # Ištriname seną žinutę ir siunčiame naują
        await query.message.delete()
        await query.message.reply_text(f"✅ Kepurė '{product_name}' (ID: {hat_id}) sėkmingai aktyvuota!")
    else:
        logger.error(f"Failed to activate product: '{product_name}' (ID: {hat_id}) by admin {query.from_user.id}")
        await query.message.reply_text(f"❌ Klaida aktyvuojant kepurę '{product_name}'!")
   

conv_add_product = ConversationHandler(
    entry_points=[CommandHandler("add_hat", add_product_start)],
    states={
        PHOTO: [MessageHandler(filters.PHOTO, add_product_photo)],
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_name)],
        DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_description)],
        PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_price)],
    },
    fallbacks=[CommandHandler("cancel", add_product_cancel)],
    allow_reentry=True,  # jei adminas nusiunčia neteisingą žinutę, gali pakartoti
)
