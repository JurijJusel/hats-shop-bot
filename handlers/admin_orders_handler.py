from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (ContextTypes,
                        ConversationHandler,
                        CallbackQueryHandler,
                        MessageHandler,
                        filters)
import sqlite3
from constants import DB_PATH
import logging

logger = logging.getLogger(__name__)


# ADMIN patvirtina apmokėjimą
async def admin_paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    order_id = int(query.data.split("_")[2])  # admin_paid_123 -> 123

    logger.info(f"Admin {query.from_user.id} confirmed payment for order #{order_id}")

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
    keyboard = [[InlineKeyboardButton("📦 IŠSIŲSTA", callback_data=f"admin_shipped_{order_id}")]]

    await query.message.edit_text(
        query.message.text, #+ f"\n\n✅ Apmokėjimas patvirtintas!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# States
TRACKING, PAYMENT, NOTES = range(3)

# ========== ENTRY POINT ==========
async def admin_shipped(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin paspaudė 'Išsiųsta' - pradedame klausti tracking number"""
    query = update.callback_query
    await query.answer()

    order_id = int(query.data.split("_")[2])  # admin_shipped_123 -> 123

    # Išsaugome order_id į context
    context.user_data['order_id'] = order_id

    # Užklausiame tracking number (PRIVALOMAS)
    await query.message.reply_text(
        f"📦 *Užsakymas #{order_id}* - Išsiuntimas\n\n"
        f"🔢 Įveskite *Tracking Number* (privalomas):",
        parse_mode="Markdown"
    )

    return TRACKING


# ========== STEP 1: TRACKING ==========
async def receive_tracking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gavome tracking number, dabar klausiam payment info"""
    tracking = update.message.text.strip()

    # Patikriname ilgį (DB limitas 50)
    if len(tracking) > 50:
        await update.message.reply_text(
            "❌ Per ilgas tracking number (max 50 simbolių).\n"
            "Įveskite trumpesnį:"
        )
        return TRACKING

    # Išsaugome
    context.user_data['tracking_number'] = tracking

    # Klausiam payment info su Skip mygtuku
    keyboard = [[InlineKeyboardButton("⏭ Praleisti", callback_data="skip_payment")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"✅ Tracking: `{tracking}`\n\n"
        f"💳 Įveskite *Payment Info* arba praleiskite:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

    return PAYMENT


# ========== STEP 2: PAYMENT INFO ==========
async def receive_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gavome payment info tekstą"""
    payment = update.message.text.strip()

    # Patikriname ilgį (DB limitas 200)
    if len(payment) > 200:
        await update.message.reply_text(
            "❌ Per ilgas payment info (max 200 simbolių).\n"
            "Įveskite trumpesnį:"
        )
        return PAYMENT

    context.user_data['payment_info'] = payment

    # Klausiam notes su Skip mygtuku
    keyboard = [[InlineKeyboardButton("⏭ Praleisti", callback_data="skip_notes")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"✅ Payment info išsaugotas\n\n"
        f"📝 Įveskite *Notes* arba praleiskite:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

    return NOTES


async def skip_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Praleido payment info"""
    query = update.callback_query
    await query.answer()

    context.user_data['payment_info'] = None

    # Klausiam notes
    keyboard = [[InlineKeyboardButton("⏭ Praleisti", callback_data="skip_notes")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.reply_text(
        f"⏭ Payment info praleistas\n\n"
        f"📝 Įveskite *Notes* arba praleiskite:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

    return NOTES


# ========== STEP 3: NOTES ==========
async def receive_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gavome notes tekstą - BAIGIAME"""
    notes = update.message.text.strip()

    # Patikriname ilgį (DB limitas 500)
    if len(notes) > 500:
        await update.message.reply_text(
            "❌ Per ilgi notes (max 500 simbolių).\n"
            "Įveskite trumpesnius:"
        )
        return NOTES

    context.user_data['notes'] = notes

    # Išsaugojam viską į DB
    return await save_to_db(update, context)


async def skip_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Praleido notes - BAIGIAME"""
    query = update.callback_query
    await query.answer()

    context.user_data['notes'] = None

    # Išsaugojam viską į DB
    return await save_to_db_callback(query, context)


# ========== FINAL: SAVE TO DB ==========
async def save_to_db(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Išsaugojam viską į DB ir užbaigiame"""
    order_id = context.user_data['order_id']
    tracking = context.user_data['tracking_number']
    payment = context.user_data.get('payment_info')
    notes = context.user_data.get('notes')

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # UPDATE orders
    cursor.execute("""
        UPDATE orders
        SET status='issiusta',
            tracking_number=?,
            payment_info=?,
            notes=?
        WHERE id=?
    """, (tracking, payment, notes, order_id))

    # Gauname user_id pranešimui
    cursor.execute("SELECT user_id FROM orders WHERE id=?", (order_id,))
    result = cursor.fetchone()
    conn.commit()
    conn.close()

    logger.info(f"Order #{order_id} shipped by admin, tracking: {tracking}")

    # Pranešimas admin'ui
    await update.message.reply_text(
        f"✅ *Užsakymas #{order_id} išsiųstas!*\n\n"
        f"📦 Tracking: `{tracking}`\n"
        f"💳 Payment: {payment or '—'}\n"
        f"📝 Notes: {notes or '—'}",
        parse_mode="Markdown"
    )

    # Pranešimas user'iui (kaip ir buvo)
    if result:
        user_id = result[0]
        await context.bot.send_message(
            chat_id=user_id,
            text=f"📦 Jūsų užsakymas #{order_id} IŠSIŲSTAS! 🚚\n"
                 f"Sekimo numeris: {tracking}\n\n"
                 f"Ačiū kad pirkote!\n\n"
                 f"📋 Peržiūrėti užsakymus: /my_orders"
        )

    # Išvalome context
    context.user_data.clear()

    return ConversationHandler.END


async def save_to_db_callback(query, context: ContextTypes.DEFAULT_TYPE):
    """Save to DB kai skip mygtuku baigiama"""
    order_id = context.user_data['order_id']
    tracking = context.user_data['tracking_number']
    payment = context.user_data.get('payment_info')
    notes = context.user_data.get('notes')

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE orders
        SET status='issiusta',
            tracking_number=?,
            payment_info=?,
            notes=?
        WHERE id=?
    """, (tracking, payment, notes, order_id))

    cursor.execute("SELECT user_id FROM orders WHERE id=?", (order_id,))
    result = cursor.fetchone()
    conn.commit()
    conn.close()

    logger.info(f"Order #{order_id} shipped by admin (via skip), tracking: {tracking}")

    await query.message.reply_text(
        f"✅ *Užsakymas #{order_id} išsiųstas!*\n\n"
        f"📦 Tracking: `{tracking}`\n"
        f"💳 Payment info: {payment or '—'}\n"
        f"📝 Notes: {notes or '—'}",
        parse_mode="Markdown"
    )

    if result:
        user_id = result[0]
        await context.bot.send_message(
            chat_id=user_id,
            text=f"📦 Jūsų užsakymas #{order_id} IŠSIŲSTAS! 🚚\n"
                 f"Tracking: {tracking}\n\n"
                 f"Ačiū kad pirkote!\n\n"
                 f"📋 Peržiūrėti užsakymus: /my_orders"
        )

    context.user_data.clear()

    return ConversationHandler.END


# ========== CONVERSATION HANDLER ==========
admin_shipped_conv_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(admin_shipped, pattern=r"admin_shipped_\d+")
    ],
    states={
        TRACKING: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_tracking)
        ],
        PAYMENT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_payment),
            CallbackQueryHandler(skip_payment, pattern="^skip_payment$")
        ],
        NOTES: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_notes),
            CallbackQueryHandler(skip_notes, pattern="^skip_notes$")
        ],
    },
    fallbacks=[],  # Nėra cancel - privalo užpildyti
)
