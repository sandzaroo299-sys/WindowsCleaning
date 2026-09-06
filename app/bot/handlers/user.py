from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters import Command
from app.config import MINI_APP_URL, BOT_TOKEN
from app.db import async_session
from app.models import User
from sqlalchemy import select

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    # Кнопка открытия Mini App
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Открыть приложение", web_app=WebAppInfo(url=MINI_APP_URL))]
    ])
    await message.answer(
        "Здравствуйте! С помощью этого бота вы можете подать заявку на мытьё окон или балкона.",
        reply_markup=kb
    )

@router.message(Command("status"))
async def cmd_status(message: Message):
    # Получаем заявки пользователя
    async with async_session() as session:
        user = await session.execute(select(User).where(User.telegram_id == message.from_user.id))
        user = user.scalar_one_or_none()
        if not user:
            await message.answer("Вы ещё не зарегистрированы. Используйте /start")
            return
        # Здесь нужно получить заявки через API или прямой запрос (для простоты опустим)
        await message.answer("Ваши заявки будут показаны в Mini App.")

@router.message(Command("pay"))
async def cmd_pay(message: Message):
    # Отправляем реквизиты (заглушка)
    await message.answer("Реквизиты для оплаты будут здесь.")