import asyncio
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import BOT_TOKEN, MINI_APP_URL
from app.db import engine, Base
from app.api.routes import router as api_router
from app.bot.main import register_handlers, dp

app = FastAPI(title="Alpinist Bot API")
app.include_router(api_router, prefix="/api")

# Подключаем статические файлы (Mini App)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")

async def on_startup():
    # Создание таблиц
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Установка команд бота
    bot = Bot(token=BOT_TOKEN)
    await bot.set_my_commands([
        BotCommand(command="start", description="Начать"),
        BotCommand(command="help", description="Помощь"),
        BotCommand(command="status", description="Мои заявки"),
        BotCommand(command="pay", description="Реквизиты"),
    ])

@app.on_event("startup")
async def startup_event():
    await on_startup()
    # Запуск бота в фоне
    asyncio.create_task(dp.start_polling(Bot(token=BOT_TOKEN), skip_updates=True))

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
