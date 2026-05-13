import os
import logging
from fastapi import FastAPI, Request
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# =====================
# CONFIG
# =====================

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

ADMIN_IDS = [123456789]  # <-- встав свій Telegram ID

FACTION_CHATS = {
    "ДБР": -5042162172,
    "НПС": -1003797046749,
    "СБС": -5173873867,
    "НАБС": -5156309034,
}

QUESTIONS = [
    "Кількість XP:",
    "Чи маєш досвід?",
    "Активність (1-10):",
    "Адекватність (1-10):",
    "Ім'я та прізвище:",
    "Вік:",
    "Чому хочеш вступити?",
]

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
app = FastAPI()

tg_app = Application.builder().token(BOT_TOKEN).build()

user_data = {}

# =====================
# START
# =====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🔎 ДБР", callback_data="ДБР"),
            InlineKeyboardButton("👮 НПС", callback_data="НПС"),
        ],
        [
            InlineKeyboardButton("🛡 СБС", callback_data="СБС"),
            InlineKeyboardButton("⚖️ НАБС", callback_data="НАБС"),
        ],
    ]

    await update.message.reply_text(
        "👋 Обери фракцію:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

# =====================
# FACTION
# =====================

async def faction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    user_data[q.from_user.id] = {
        "faction": q.data,
        "index": 0,
        "answers": []
    }

    await q.edit_message_text(
        f"✅ Обрано: {q.data}\n\nНапиши /next щоб почати анкету"
    )

# =====================
# NEXT QUESTION
# =====================

async def next_q(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    if uid not in user_data:
        await update.message.reply_text("Спочатку /start")
        return

    i = user_data[uid]["index"]

    if i >= len(QUESTIONS):
        await finish(update, context)
        return

    await update.message.reply_text(QUESTIONS[i])

# =====================
# ANSWERS
# =====================

async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    if uid not in user_data:
        return

    data = user_data[uid]
    data["answers"].append(update.message.text)
    data["index"] += 1

    if data["index"] < len(QUESTIONS):
        await update.message.reply_text(QUESTIONS[data["index"]])
    else:
        await finish(update, context)

# =====================
# FINISH
# =====================

async def finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    data = user_data.get(uid)

    if not data:
        return

    faction = data["faction"]
    answers = data["answers"]

    user = update.effective_user

    text = f"🟢 Нова заявка: {faction}\n"
    text += f"User: @{user.username}\n\n"

    for i, ans in enumerate(answers):
        q = QUESTIONS[i] if i < len(QUESTIONS) else ""
        text += f"{i+1}. {q}\n{ans}\n\n"

    # send to faction chat
    await bot.send_message(
        chat_id=FACTION_CHATS[faction],
        text=text[:4000]
    )

    # notify admin
    for admin in ADMIN_IDS:
        try:
            await bot.send_message(
                chat_id=admin,
                text=f"🔔 Нова заявка в {faction} від @{user.username}"
            )
        except:
            pass

    await update.message.reply_text("✅ Заявку подано!")

    user_data.pop(uid, None)

# =====================
# HANDLERS
# =====================

tg_app.add_handler(CommandHandler("start", start))
tg_app.add_handler(CommandHandler("next", next_q))
tg_app.add_handler(CallbackQueryHandler(faction))
tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, answer))

# =====================
# WEBHOOK
# =====================

@app.post("/")
async def webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, bot)

    await tg_app.process_update(update)
    return {"ok": True}

# =====================
# STARTUP
# =====================

@app.on_event("startup")
async def startup():
    await bot.set_webhook(f"{WEBHOOK_URL}/")
    print("Webhook set!")
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("bot:app", host="0.0.0.0", port=10000)

