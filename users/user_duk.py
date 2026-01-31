from telegram import Update
from telegram.ext import ContextTypes
from admin.admin_ban_user import check_blacklist


@check_blacklist
async def questions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Dažniausi klausimai ir kontaktinė informacija
    """
    info_text = (
        "❓ <b>DAŽNIAUSI KLAUSIMAI</b>\n\n"

        "<b>Kiek trunka pristatymas?</b>\n"
        "→ 3-5 darbo dienos Lietuvoje priklauso nuot siuntos tarnybos\n\n"

        "<b>Kada gausiu patvirtinimą?</b>\n"
        "→ Per 1 - 8 val. nuo užsakymo pateikimo\n\n"

        "<b>Ar galima grąžinti ar pakeist prekę?</b>\n"
        "→ Taip, susisiekite dėl užsakymo pekeitimo ar grąžinimo\n\n"

        "<b>Kiek kainuoja pristatymas?</b>\n"
        "→ Lietuvoje pristatymas nemokamas\n\n"

        "<b>Ar galima atsiimti pačiam?</b>\n"
        "→ Taip, (susisiekite dėl adreso)"

        "<b>Kokie mokėjimo būdai?</b>\n"
        "→ Banko pavedimas / Revolut\n\n"

        "<b>Kada reikia mokėti?</b>\n"
        "→ Po užsakymo patvirtinimo\n\n"

        "<b>Ar siunčiate į užsienį?</b>\n"
        "→ Taip, susisiekite dėl kainos\n\n"

        "━━━━━━━━━━━━━━━━━━━━━\n\n"

        "📞 <b>KONTAKTAI</b>\n\n"
        "📧 El. paštas: viktorija.jusel@gmail.com\n"
        "📱 Telefonas: +370 653 73195\n"
        "👤 Facebook: https://www.facebook.com/feltingmywaypirtieskepures\n\n"

        "Mielai atsakysime į visus klausimus! 😊"
    )

    await update.message.reply_text(info_text, parse_mode='HTML')
