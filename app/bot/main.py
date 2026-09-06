from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from app.bot.handlers import user, worker, admin

dp = Dispatcher(storage=MemoryStorage())

def register_handlers():
    user.register_handlers(dp)
    worker.register_handlers(dp)
    admin.register_handlers(dp)