import asyncio
import logging
import time

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

BOT_TOKEN = "ВСТАВ_ТОКЕН"

ADMIN_IDS = [123456789]  # <-- свій Telegram ID сюди

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# =========================
# DATA
# =========================

FACTIONS = ["ДБР", "НПС", "СБС", "НАБС"]

QUESTIONS = [
    "Кількість XP у вас:",
    "Чи маєте досвід?",
    "Ваша активність (1-10):",
    "Ваш вік:",
    "Чому хочете вступити?:"
]

user_state = {}
cooldowns = {}

# =========================
# ANTI SPAM
# =========================

def is_spam(user_id):
    now = time.time()
    last = cooldowns.get(user_id, 0)

    if now - last < 3:
        return True

    cooldowns[user_id] = now
    return False

# =========================
# START MENU
# =========================

@dp.message(Command("start"))
async def start(message: types.Message):
    if is_spam(message.from_user.id):
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔎 ДБР", callback_data="ДБР")],
        [InlineKeyboardButton(text="👮 НПС", callback_data="НПС")],
        [InlineKeyboardButton(text="🛡 СБС", callback_data="СБС")],
        [InlineKeyboardButton(text="⚖️ НАБС", callback_data="НАБС")]
    ])

    await message.answer("🔥 Обери фракцію:", reply_markup=kb)

# =========================
# FACTION SELECT
# =========================

@dp.callback_query(F.data.in_(FACTIONS))
async def faction(call: types.CallbackQuery):
    user_state[call.from_user.id] = {
        "faction": call.data,
        "q": 0,
        "answers": []
    }

    await call.message.answer(
        f"✅ Ти обрав {call.data}\n\nПочинаємо анкету..."
    )

    await ask_question(call.from_user.id)
    await call.answer()

# =========================
# ASK QUESTION
# =========================

async def ask_question(user_id):
    state = user_state[user_id]
    q_index = state["q"]

    if q_index < len(QUESTIONS):
        await bot.send_message(
            user_id,
            QUESTIONS[q_index]
        )
    else:
        await finish(user_id)

# =========================
# ANSWERS
# =========================

@dp.message()
async def answer(message: types.Message):
    user_id = message.from_user.id

    if user_id not in user_state:
        return

    if is_spam(user_id):
        return

    state = user_state[user_id]

    state["answers"].append(message.text)
    state["q"] += 1

    await ask_question(user_id)

# =========================
# FINISH
# =========================

async def finish(user_id):
    state = user_state[user_id]

    text = f"🚨 НОВА ЗАЯВКА\nФракція: {state['faction']}\n\n"

    for i, ans in enumerate(state["answers"]):
        text += f"{QUESTIONS[i]} {ans}\n"

    # send to admins
    for admin in ADMIN_IDS:
        await bot.send_message(admin, text)

    await bot.send_message(user_id, "✅ Заявку подано!")

    user_state.pop(user_id, None)

# =========================
# ADMIN PANEL
# =========================

@dp.message(Command("admin"))
async def admin(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return

    await message.answer("🛠 Адмін панель активна")

# =========================
# RUN
# =========================

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
