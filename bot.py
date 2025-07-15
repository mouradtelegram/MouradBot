from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
import logging

# Aktiver logging
logging.basicConfig(level=logging.INFO)

# Eksempelbrukere
brukere = {}

# Start-kommando
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in brukere:
        brukere[user_id] = {"poeng": 0}
    knapp = InlineKeyboardMarkup([[InlineKeyboardButton("Få 10 poeng", callback_data="verv")]])
    await update.message.reply_text("Velkommen til MouradBot! Trykk for å få poeng:", reply_markup=knapp)

# Callback når noen trykker på knappen
async def knappetrykk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    brukere[user_id]["poeng"] += 10
    await query.edit_message_text(f"🎉 Du har nå {brukere[user_id]['poeng']} poeng!")

# Poengstatus
async def poeng(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    poeng = brukere.get(user_id, {}).get("poeng", 0)
    await update.message.reply_text(f"Du har {poeng} poeng.")

# Start bot
if __name__ == "__main__":
    app = ApplicationBuilder().token("DIN_TOKEN_HER").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("poeng", poeng))
    app.add_handler(CallbackQueryHandler(knappetrykk))
    app.run_polling()
