import os
import time
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
    ConversationHandler,
)

# =======================
# CONFIG
# =======================

BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_IDS = [123456789]  # <-- заміни на свій Telegram ID

FACTION_CHATS = {
    "ДБР": -5042162172,
    "НПС": -1003797046749,
    "СБС": -5173873867,
    "НАБС": -5156309034,
}

QUESTIONS = [
    "Кількість XP у вас за поліцію:",
    "Чи маєте досвід роботи?",
    "Ваш вік:",
    "Ваша активність (1-10):",
    "Чому хочете вступити?",
]

# антиспам
last_msg_time = {}

CHOOSE, ASKING = range(2)

logging.basicConfig(level=logging.INFO)

# =======================
# START
# =======================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔎 ДБР", callback_data="ДБР")],
        [InlineKeyboardButton("👮 НПС", callback_data="НПС")],
        [InlineKeyboardButton("🛡 СБС", callback_data="СБС")],
        [InlineKeyboardButton("⚖️ НАБС", callback_data="НАБС")],
    ]

    await update.message.reply_text(
        "👋 Обери фракцію:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return CHOOSE

# =======================
# FACTION SELECT
# =======================

async def choose(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    context.user_data["faction"] = q.data
    context.user_data["answers"] = []
    context.user_data["index"] = 0

    await q.edit_message_text(
        f"✅ Фракція: {q.data}\n\n{QUESTIONS[0]}"
    )
    return ASKING

# =======================
# ANSWERS + ANTI-SPAM
# =======================

async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    now = time.time()

    # антиспам (1 повідомлення / 2 сек)
    if user_id in last_msg_time and now - last_msg_time[user_id] < 2:
        await update.message.reply_text("⏳ Не спам!")
        return ASKING

    last_msg_time[user_id] = now

    answers = context.user_data["answers"]
    index = context.user_data["index"]

    answers.append(update.message.text)
    index += 1

    context.user_data["answers"] = answers
    context.user_data["index"] = index

    if index < len(QUESTIONS):
        await update.message.reply_text(QUESTIONS[index])
        return ASKING

    await finish(update, context)
    return ConversationHandler.END

# =======================
# FINISH + SEND
# =======================

async def finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    faction = context.user_data["faction"]
    answers = context.user_data["answers"]

    text = f"📩 Нова заявка: {faction}\n\n"

    for q, a in zip(QUESTIONS, answers):
        text += f"{q}\n➡️ {a}\n\n"

    # відправка у фракцію
    await context.bot.send_message(
        chat_id=FACTION_CHATS[faction],
        text=text,
    )

    # адмінам
    for admin in ADMIN_IDS:
        await context.bot.send_message(
            chat_id=admin,
            text="🚨 Нова заявка відправлена"
        )

    await update.message.reply_text("✅ Заявку відправлено!")

# =======================
# CANCEL
# =======================

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Скасовано")
    return ConversationHandler.END

# =======================
# MAIN
# =======================

def main():
    if not BOT_TOKEN:
        raise Exception("BOT_TOKEN missing")

    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSE: [CallbackQueryHandler(choose)],
            ASKING: [MessageHandler(filters.TEXT & ~filters.COMMAND, answer)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
