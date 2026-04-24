import asyncio
from os import getenv
from dotenv import load_dotenv
import logging
import sys
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database import init_db, add_debt, get_debts, delete_debt

load_dotenv()

TOKEN=getenv("BOT_TOKEN")

# Bot tokeningizni bu yerga yozing
TOKEN = "8766616843:AAEcpmNK3EptHAzRvMYPqenc3WYQnz9hfik"

bot = Bot(token=TOKEN)
dp = Dispatcher()


# Savol-javob holatlari
class DebtState(StatesGroup):
    kimdan = State()
    miqdori = State()
    sana = State()


# Tugmalar
def main_menu():
    buttons = [
        [InlineKeyboardButton(text="➕ Qarz qo'shish", callback_data="add_debt")],
        [InlineKeyboardButton(text="📜 Qarzlar ro'yxati", callback_data="list_debts")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer("Assalomu alaykum! Qarz daftari botiga xush kelibsiz.", reply_markup=main_menu())


# Qarz qo'shishni boshlash
@dp.callback_query(F.data == "add_debt")
async def start_adding(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Kimdan qarz oldingiz? (Ism yozing):")
    await state.set_state(DebtState.kimdan)


@dp.message(DebtState.kimdan)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(kimdan=message.text)
    await message.answer("Qancha qarz oldingiz? (Masalan: 100 ming so'm):")
    await state.set_state(DebtState.miqdori)


@dp.message(DebtState.miqdori)
async def process_amount(message: types.Message, state: FSMContext):
    await state.update_data(miqdori=message.text)
    await message.answer("Qachon qaytarishingiz kerak? (Sana yozing):")
    await state.set_state(DebtState.sana)


@dp.message(DebtState.sana)
async def process_date(message: types.Message, state: FSMContext):
    data = await state.get_data()
    add_debt(message.from_user.id, data['kimdan'], data['miqdori'], message.text)
    await state.clear()
    await message.answer("✅ Qarz muvaffaqiyatli saqlandi!", reply_markup=main_menu())


# Qarzlar ro'yxatini chiqarish
@dp.callback_query(F.data == "list_debts")
async def show_debts(callback: types.CallbackQuery):
    debts = get_debts(callback.from_user.id)
    if not debts:
        await callback.answer("Hozircha qarzlar yo'q.", show_alert=True)
        return

    text = "📜 **Sizning qarzlaringiz:**\n\n"
    buttons = []
    for d in debts:
        text += f"👤 {d[1]} | 💰 {d[2]} | 📅 {d[3]}\n"
        buttons.append([InlineKeyboardButton(text=f"❌ {d[1]} - o'chirish", callback_data=f"del_{d[0]}")])

    buttons.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")


# Qarzni o'chirish
@dp.callback_query(F.data.startswith("del_"))
async def remove_debt(callback: types.CallbackQuery):
    debt_id = callback.data.split("_")[1]
    delete_debt(debt_id)
    await callback.answer("Qarz o'chirildi!")
    await show_debts(callback)  # Ro'yxatni yangilash


@dp.callback_query(F.data == "back")
async def go_back(callback: types.CallbackQuery):
    await callback.message.edit_text("Asosiy menyu:", reply_markup=main_menu())


async def main():
    init_db()  # Bazani yaratish
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())