from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
import logging
import re

# Bot-token og admin-ID
BOT_TOKEN = "7552419253:AAGo1cYWjM-Lkl21W10U2Okc3BJqJUgeaV0"
ADMIN_ID = 7552419253
STRIPE_URL = "https://buy.stripe.com/6oU4gydqR0V02sabJM38400"

# Logging
logging.basicConfig(level=logging.INFO)

# Midlertidig bruker-database
brukere = {}

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in brukere:
        brukere[user_id] = {"poeng": 0, "aktivert": True, "likt": 0}
    await meny(update, context)

# Meny
async def meny(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    bruker = brukere.get(user_id, {"poeng": 0, "aktivert": True, "likt": 0})

    if not bruker["aktivert"]:
        keyboard = [[InlineKeyboardButton("💳 Aktiver konto (250 kr)", url=STRIPE_URL)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("❌ Du må aktivere kontoen din først. Trykk under for å betale:", reply_markup=reply_markup)
        return

    keyboard = [
        [InlineKeyboardButton("🎬 Send YouTube-lenke for å få poeng", callback_data="yt")],
        [InlineKeyboardButton("👥 Verv en venn", callback_data="verv")],
        [InlineKeyboardButton("📊 Mine poeng", callback_data="poeng")],
        [InlineKeyboardButton("💸 Uttak", callback_data="uttak")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Velg et alternativ:", reply_markup=reply_markup)

# Knappetrykk
async def knappetrykk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    bruker = brukere.get(user_id, {"poeng": 0, "aktivert": True, "likt": 0})

    if query.data == "poeng":
        await query.edit_message_text(f"📊 Du har {bruker['poeng']} poeng.")

    elif query.data == "verv":
        bruker["poeng"] += 50
        await query.edit_message_text("👥 Du fikk 50 poeng for å verve en venn!")

    elif query.data == "uttak":
        if bruker["poeng"] < 500:
            await query.edit_message_text("🚫 Du må ha minst 500 poeng for å kunne ta ut penger.")
        else:
            bruker["aktivert"] = False
            await query.edit_message_text(
                "💳 For å fullføre uttaket og fortsette å bruke tjenesten, må du betale 250 kr:",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Betal nå", url=STRIPE_URL)]])
            )

    elif query.data == "yt":
        await query.edit_message_text("📩 Send meg en YouTube-lenke som melding!")

    elif query.data == "liker":
        bruker["poeng"] += 10
        bruker["likt"] += 1
        if bruker["likt"] % 5 == 0:
            bruker["poeng"] += 100
        await query.edit_message_text(f"✅ Du fikk poeng! Total: {bruker['poeng']}")

# YouTube-lenker
async def melding(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    yt_match = re.search(r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/\S+", text)
    if yt_match:
        keyboard = [
            [InlineKeyboardButton("👍 Liker", callback_data="liker"), InlineKeyboardButton("👎 Liker ikke", callback_data="liker")]
        ]
        await update.message.reply_text("Hva synes du om videoen?", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text("❓ Jeg forstår bare YouTube-lenker eller bruk menyen.")

# Aktiver bruker (admin)
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
        await update.message.reply_text("🚫 Bruker ikke funnet.")

# Start boten
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("aktiver", aktiver))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, melding))
    app.add_handler(CallbackQueryHandler(knappetrykk))
    app.run_polling()
