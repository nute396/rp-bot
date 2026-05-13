import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN missing")

logging.basicConfig(level=logging.INFO)

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
# CALLBACK
# =====================

async def faction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text(f"✅ Обрано: {q.data}")

# =====================
# SIMPLE ANSWER
# =====================

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"📝 Отримано: {update.message.text}")

# =====================
# MAIN APP
# =====================

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(faction))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
