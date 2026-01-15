from config import BOT_TOKEN
from telegram.ext import (ApplicationBuilder,
                        CommandHandler,
                        CallbackQueryHandler,
                        filters,
                        MessageHandler)
from admin.admin_show_users import admin_show_users
from admin.admin_info import admin_info
from admin.admin_orders import admin_show_orders, admin_show_orders_10, admin_show_orders_status
from admin.admin_add_products import (conv_add_product,
                                admin_show_products,
                                activate_hat,
                                delete_hat)
from users.user_help import user_help
from users.user_orders import my_orders
from handlers.admin_orders_handler import admin_shipped_conv_handler
from handlers.user_fallback import unknown_message
from handlers.user_checkout import conversation_handler, payment_confirmed
from handlers.admin_orders_handler import admin_paid, admin_shipped
from handlers.cart_handler import show_cart, remove_from_cart, add_to_cart
from handlers.start_handler import (start,
                                text_show_products,
                                text_show_cart)
import logging
import logging.config
from logging_err.logging_config import LOGGING_CONFIG

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

TOKEN = BOT_TOKEN


if __name__ == "__main__":
    try:
        logger.info("Botas inicializuojamas...")
        app = ApplicationBuilder().token(TOKEN).build()

        # Command handler /start
        app.add_handler(CommandHandler("start", start))

        # Tekstiniai mygtukai (fiksuoti apačioje)
        app.add_handler(MessageHandler(filters.Regex("^🧢 Kepurės$"), text_show_products))
        app.add_handler(MessageHandler(filters.Regex("^🛒 Krepšelis$"), text_show_cart))

        # Callback handler
        app.add_handler(CallbackQueryHandler(show_cart, pattern="show_cart"))
        app.add_handler(CallbackQueryHandler(add_to_cart, pattern="addcart_"))
        app.add_handler(CallbackQueryHandler(remove_from_cart, pattern="remove_"))

        # USER handlers Checkout
        app.add_handler(conversation_handler)
        app.add_handler(CallbackQueryHandler(payment_confirmed, pattern=r"paid_\d+"))
        app.add_handler(CommandHandler("my_orders", my_orders))
        app.add_handler(CommandHandler("help", user_help))

        # admin handlers
        app.add_handler(conv_add_product)
        app.add_handler(CommandHandler("show_hats", admin_show_products))
        app.add_handler(CallbackQueryHandler(delete_hat, pattern="delete_hat_"))
        app.add_handler(CallbackQueryHandler(activate_hat, pattern="activate_hat_"))
        app.add_handler(CommandHandler("info", admin_info))
        app.add_handler(CommandHandler("show_orders", admin_show_orders))
        app.add_handler(CommandHandler("show_orders_10", admin_show_orders_10))
        app.add_handler(CommandHandler("show_orders_status", admin_show_orders_status))
        app.add_handler(CommandHandler("show_users", admin_show_users))

        # Admino užsakymų mygtukai („APMOKĖTA“ / „IŠSIŲSTA“)
        app.add_handler(admin_shipped_conv_handler)
        app.add_handler(CallbackQueryHandler(admin_paid, pattern=r"admin_paid_\d+"))
        app.add_handler(CallbackQueryHandler(admin_shipped, pattern=r"admin_shipped_\d+"))

        # PASKUTINIS handler - fallback neatpažintoms žinutėms
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown_message))

        logger.info("Visi handler'iai užregistruoti")
        logger.info("Botas paleistas ir veikia...")
        print("Botas paleistas...")
        app.run_polling()

    except KeyboardInterrupt:
        logger.info("Botas sustabdytas (Ctrl+C)")
    except Exception as e:
        logger.error(f"Kritinė klaida paleidžiant botą: {e}", exc_info=True)
        raise
    finally:
        logger.info("Botas uždaromas...")
