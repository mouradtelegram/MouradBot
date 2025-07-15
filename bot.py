
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import json
import os

DATAFIL = "brukere.json"
ADMIN_ID = 7552419253  # Mourad
STRIPE_URL = "https://buy.stripe.com/6oU4gydqR0V02sabJM38400"

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
        f"🔗 Din vervelenke:

https://t.me/{context.bot.username}?start={kode}

"
        f"👉 Del den med en venn. Når de starter boten, får du 50 poeng!"
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    args = context.args
    if user_id not in brukere:
        brukere[user_id] = {"poeng": 0, "aktivert": False}
        # sjekk for referral
        if args and args[0].startswith("ref_"):
            referrer = args[0].split("_")[1]
            if referrer != user_id and referrer in brukere:
                brukere[referrer]["poeng"] += 50
                await context.bot.send_message(chat_id=int(referrer), text="🎉 Du har fått 50 poeng for å verve en venn!")
        lagre_data(brukere)
    await update.message.reply_text(
        "Velkommen! Du kan tjene poeng ved å gjøre små oppdrag. Skriv /oppdrag for å starte!"
    )


async def oppdrag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if not brukere.get(user_id, {}).get("aktivert"):
        keyboard = [
            [InlineKeyboardButton("🔐 Betal 250 kr", url=STRIPE_URL)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("❌ Du må aktivere kontoen din først:", reply_markup=reply_markup)
        return
    brukere.setdefault(user_id, {"poeng": 0, "aktivert": False})
    brukere[user_id]["poeng"] += 10
    lagre_data(brukere)
    video_link = choice(['https://youtu.be/6Ejga4kJUts', 'https://youtu.be/dQw4w9WgXcQ', 'https://youtu.be/kJQP7kiw5Fk', 'https://youtu.be/3JZ_D3ELwOQ', 'https://youtu.be/2Vv-BfVoq4g'])
    await update.message.reply_text(
        f"✅ Oppdrag i dag:

👉 Gå inn og lik denne videoen på YouTube:
{video_link}

10 poeng er lagt til kontoen din!"
    )


async def poeng(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    poeng = brukere.get(user_id, {}).get("poeng", 0)
    await update.message.reply_text(f"💰 Du har {poeng} poeng.")


async def uttak(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if not brukere.get(user_id, {}).get("aktivert"):
        keyboard = [
            [InlineKeyboardButton("🔐 Betal 250 kr", url=STRIPE_URL)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("❌ Du må aktivere kontoen din først:", reply_markup=reply_markup)
        return
    poeng = brukere.get(user_id, {}).get("poeng", 0)
    if poeng >= 200:
        brukere[user_id]["poeng"] -= 200
        lagre_data(brukere)
        await update.message.reply_text("📩 Uttak registrert! Du får pengene manuelt innen 24 timer.")
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"🔔 Bruker @{update.effective_user.username or user_id} ba om uttak!")
    else:
        keyboard = [
            [InlineKeyboardButton("📈 Tjen mer poeng", callback_data="oppdrag")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(f"⚠️ Du har bare {poeng} poeng. Du trenger 200 for uttak.", reply_markup=reply_markup)

async def meny(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎯 Få oppdrag", callback_data="oppdrag")],
        [InlineKeyboardButton("💰 Se poeng", callback_data="poeng")],
        [InlineKeyboardButton("📤 Be om uttak", callback_data="uttak")],
        [InlineKeyboardButton("🔐 Betal 250 kr", url=STRIPE_URL)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Hva vil du gjøre?", reply_markup=reply_markup)

async def knapp_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "oppdrag":
        await oppdrag(query, context)
    elif query.data == "poeng":
        await poeng(query, context)
    elif query.data == "uttak":
        await uttak(query, context)

async def betal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔐 Betal 250 kr", url=STRIPE_URL)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Klikk på knappen under for å aktivere kontoen din:", reply_markup=reply_markup)


async def aktiver(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    brukere.setdefault(user_id, {"poeng": 0, "aktivert": False})
    brukere[user_id]["aktivert"] = True
    lagre_data(brukere)
    await update.message.reply_text("✅ Kontoen din er nå aktivert!")

def main():
    app = ApplicationBuilder().token("7552419253:AAGo1cYWjM-Lkl21W10U2Okc3BJqJUgeaV0").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("oppdrag", oppdrag))
    app.add_handler(CommandHandler("poeng", poeng))
    app.add_handler(CommandHandler("uttak", uttak))
    app.add_handler(CommandHandler("betal", betal))
    
    app.add_handler(CommandHandler("aktiver120619", aktiver))

    
    app.add_handler(CommandHandler("meny", meny))
    app.add_handler(CallbackQueryHandler(knapp_handler))
    
    app.add_handler(CommandHandler("verv", verv))
    app.add_handler(CommandHandler("meny", meny))
    app.add_handler(CallbackQueryHandler(knapp_handler))
    app.run_polling()




if __name__ == '__main__':
    main()
