from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
import logging
import re

# Aktiver logging
logging.basicConfig(level=logging.INFO)

# Bot-token
TOKEN = "123456789:ABCdefGhIJKLmnoPQRstuVwxy"
STRIPE_URL = "https://buy.stripe.com/6oU4gydqR0V02sabJM38400"
ADMIN_ID = 123456789  # Bytt til din Telegram-ID

brukere = {}

# Start-kommando
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in brukere:
        brukere[user_id] = {"poeng": 0, "aktivert": False}
    await meny(update, context)

# Menyfunksjon
async def meny(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    bruker = brukere.get(user_id, {"poeng": 0, "aktivert": False})

    if not bruker["aktivert"]:
        keyboard = [[InlineKeyboardButton("🔐 Aktiver konto (250 kr)", url=STRIPE_URL)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("❌ Du må aktivere kontoen din for å begynne."

Trykk under for å betale:", reply_markup=reply_markup)
        return

    keyboard = [
        [InlineKeyboardButton("🎯 Få poeng", callback_data="oppdrag")],
        [InlineKeyboardButton("🎥 YouTube", callback_data="yt")],
        [InlineKeyboardButton("💰 Poeng", callback_data="poeng")],
        [InlineKeyboardButton("🏧 Uttak", callback_data="uttak")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Velg et alternativ:", reply_markup=reply_markup)

# Knappetrykk
async def knappetrykk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)

    if not brukere.get(user_id, {}).get("aktivert"):
        await query.edit_message_text("❌ Du må aktivere kontoen din først.")
        return

    if query.data == "oppdrag":
        brukere[user_id]["poeng"] += 10
        await query.edit_message_text(f"✅ Du fikk 10 poeng! Total: {brukere[user_id]['poeng']}")
    elif query.data == "poeng":
        await query.edit_message_text(f"💰 Du har {brukere[user_id]['poeng']} poeng.")
    elif query.data == "uttak":
        await query.edit_message_text("🏧 Uttaksforespørsel mottatt! En admin vil kontakte deg.")
    elif query.data == "yt":
        await query.edit_message_text("🎥 Send meg en YouTube-lenke som melding!")

# Meldinger
async def melding(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    yt_match = re.search(r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/\S+", text)
    if yt_match:
        await update.message.reply_text("✅ YouTube-lenke oppdaget! Takk for at du delte.")
    else:
        await update.message.reply_text("❓ Jeg forstår bare YouTube-lenker eller bruk menyen.")

# Aktivering av bruker (admin)
async def aktiver(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Du har ikke tilgang.")
        return
    if not context.args:
        await update.message.reply_text("Bruk: /aktiver <bruker_id>")
        return
    target_id = context.args[0]
    if target_id in brukere:
        brukere[target_id]["aktivert"] = True
        await update.message.reply_text(f"✅ Bruker {target_id} er nå aktivert.")
    else:
        await update.message.reply_text("Bruker ikke funnet.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("aktiver", aktiver))
    app.add_handler(CallbackQueryHandler(knappetrykk))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, melding))
    app.run_polling()
