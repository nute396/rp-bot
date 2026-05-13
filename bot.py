import os
import logging
from fastapi import FastAPI, Request
from telegram import Update, Bot
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

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing in environment variables")

ADMIN_IDS = [123456789]  # <-- заміни на свій ID

bot = Bot(token=BOT_TOKEN)
app = FastAPI()

logging.basicConfig(level=logging.INFO)

tg_app = Application.builder().token(BOT_TOKEN).build()

# =====================
# START
# =====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Бот працює!")

# =====================
# HANDLER EXAMPLE
# =====================

tg_app.add_handler(CommandHandler("start", start))

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
# SET WEBHOOK
# =====================

@app.on_event("startup")
async def startup():
    await bot.set_webhook(f"{WEBHOOK_URL}/")
    logging.info("Webhook set successfully")

# =====================
# OPTIONAL LOCAL RUN (для ПК)
# =====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("bot:app", host="0.0.0.0", port=10000)
