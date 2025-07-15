
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import json, os
from random import choice

DATAFIL = "brukere.json"
ADMIN_ID = 7552419253
STRIPE_URL = "https://buy.stripe.com/6oU4gydqR0V02sabJM38400"
VIDEOER = [
    "https://youtu.be/6Ejga4kJUts",
    "https://youtu.be/dQw4w9WgXcQ",
    "https://youtu.be/kJQP7kiw5Fk",
    "https://youtu.be/3JZ_D3ELwOQ",
    "https://youtu.be/2Vv-BfVoq4g"
]

def lagre_data(brukere):
    with open(DATAFIL, "w") as f:
        json.dump(brukere, f)

def last_data():
    if os.path.exists(DATAFIL):
        with open(DATAFIL, "r") as f:
            return json.load(f)
    return {}

brukere = last_data()

async def verv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    kode = f"ref_{user_id}"
    await update.message.reply_text(
        f"🔗 Din vervelenke:\n\nhttps://t.me/{context.bot.username}?start={kode}\n\n"
        f"👉 Del den med en venn. Når de starter boten, får du 50 poeng!"
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    args = context.args
    if user_id not in brukere:
        brukere[user_id] = {"poeng": 0, "aktivert": False}
        if args and args[0].startswith("ref_"):
            referrer = args[0].split("_")[1]
            if referrer != user_id and referrer in brukere:
                brukere[referrer]["poeng"] += 50
                await context.bot.send_message(chat_id=int(referrer), text="🎉 Du har fått 50 poeng for å verve en venn!")
        lagre_data(brukere)
    await update.message.reply_text("Velkommen! Du kan tjene poeng ved å gjøre små oppdrag. Skriv /meny for å starte.")

async def oppdrag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if not brukere.get(user_id, {}).get("aktivert"):
        keyboard = [[InlineKeyboardButton("🔐 Betal 250 kr", url=STRIPE_URL)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("❌ Du må aktivere kontoen din først:", reply_markup=reply_markup)
        return
    brukere.setdefault(user_id, {"poeng": 0, "aktivert": False})
    brukere[user_id]["poeng"] += 10
    lagre_data(brukere)
    video_link = choice(VIDEOER)
    await update.message.reply_text(
        f"✅ Oppdrag i dag:\n\n👉 Gå inn og lik denne videoen:\n{video_link}\n\n10 poeng er lagt til kontoen din!"
    )

async def poeng(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    poeng = brukere.get(user_id, {}).get("poeng", 0)
    await update.message.reply_text(f"💰 Du har {poeng} poeng.")

async def uttak(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if not brukere.get(user_id, {}).get("aktivert"):
        keyboard = [[InlineKeyboardButton("🔐 Betal 250 kr", url=STRIPE_URL)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("❌ Du må aktivere kontoen din før du kan gjøre uttak.", reply_markup=reply_markup)
        return
    await update.message.reply_text("✅ Uttak forespørsel mottatt. Du vil bli kontaktet manuelt for utbetaling.")

async def aktiver(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id == str(ADMIN_ID):
        if context.args:
            mål_id = context.args[0]
            if mål_id in brukere:
                brukere[mål_id]["aktivert"] = True
                lagre_data(brukere)
                await update.message.reply_text(f"✅ Bruker {mål_id} er nå aktivert.")
                return
    await update.message.reply_text("❌ Du har ikke tillatelse.")

async def meny(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎯 Oppdrag", callback_data="oppdrag")],
        [InlineKeyboardButton("💰 Sjekk poeng", callback_data="poeng")],
        [InlineKeyboardButton("🏧 Uttak", callback_data="uttak")],
        [InlineKeyboardButton("👥 Verv en venn", callback_data="verv")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Velg et alternativ:", reply_markup=reply_markup)

async def knappetrykk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == "oppdrag":
        await oppdrag(update, context)
    elif data == "poeng":
        await poeng(update, context)
    elif data == "uttak":
        await uttak(update, context)
    elif data == "verv":
        await verv(update, context)

app = ApplicationBuilder().token("YOUR_BOT_TOKEN_HERE").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("oppdrag", oppdrag))
app.add_handler(CommandHandler("poeng", poeng))
app.add_handler(CommandHandler("uttak", uttak))
app.add_handler(CommandHandler("verv", verv))
app.add_handler(CommandHandler("aktiver", aktiver))
app.add_handler(CommandHandler("meny", meny))
app.add_handler(CallbackQueryHandler(knappetrykk))
app.run_polling()
