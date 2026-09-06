from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from app.config import ADMIN_IDS
from app.services.qr import generate_qr_code

router = Router()

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

@router.message(Command("admin"))
async def cmd_admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("Нет прав.")
        return
    await message.answer("Админ-панель: /requests, /notify, /add_building и др.")

@router.message(Command("add_building"))
async def cmd_add_building(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("Нет прав.")
        return
    # Здесь будет логика добавления дома через FSM или просто инструкция
    await message.answer("Добавление дома будет реализовано через Mini App.")

@router.message(Command("generate_qr"))
async def cmd_generate_qr(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("Нет прав.")
        return
    # Пример: /generate_qr 1
    try:
        building_id = int(message.text.split()[1])
        qr_image_path = generate_qr_code(building_id)
        # Отправить фото
        await message.answer_photo(photo=open(qr_image_path, 'rb'))
    except Exception as e:
        await message.answer(f"Ошибка: {e}")