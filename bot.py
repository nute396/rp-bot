import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# =====================
# START
# =====================

@dp.message(Command("start"))
async def start(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(text="🔎 ДБР", callback_data="ДБР"),
            types.InlineKeyboardButton(text="👮 НПС", callback_data="НПС"),
        ],
        [
            types.InlineKeyboardButton(text="🛡 СБС", callback_data="СБС"),
            types.InlineKeyboardButton(text="⚖️ НАБС", callback_data="НАБС"),
        ],
    ])

    await message.answer("👋 Обери фракцію:", reply_markup=keyboard)

# =====================
# CALLBACK
# =====================

@dp.callback_query()
async def callback(call: types.CallbackQuery):
    await call.message.edit_text(f"✅ Обрано: {call.data}")

# =====================
# MAIN
# =====================

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
