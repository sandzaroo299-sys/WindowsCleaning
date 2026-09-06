from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from app.config import WORKER_IDS, ADMIN_IDS

router = Router()

def is_worker_or_admin(user_id: int) -> bool:
    return user_id in WORKER_IDS or user_id in ADMIN_IDS

@router.message(Command("my_requests"))
async def cmd_worker_requests(message: Message):
    if not is_worker_or_admin(message.from_user.id):
        await message.answer("У вас нет доступа к этой команде.")
        return
    # Здесь должна быть логика получения заявок, доступных работнику
    await message.answer("Список заявок будет здесь (реализуем позже).")

@router.message(Command("set_status"))
async def cmd_set_status(message: Message):
    if not is_worker_or_admin(message.from_user.id):
        await message.answer("У вас нет доступа.")
        return
    # Пример: /set_status 5 completed
    try:
        _, request_id, new_status = message.text.split()
        await message.answer(f"Статус заявки {request_id} изменён на {new_status}")
    except:
        await message.answer("Используйте: /set_status <id> <статус>")