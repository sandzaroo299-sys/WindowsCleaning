import asyncio
import json
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import BOT_TOKEN, MINI_APP_URL
from app.db import engine, Base, async_session
from app.models import Building, Apartment
from app.api.routes import router as api_router
from app.bot.main import register_handlers, dp

app = FastAPI(title="Alpinist Bot API")
app.include_router(api_router, prefix="/api")

# Статика
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")

async def load_houses_from_file():
    houses_file = Path("data/houses.json")
    if not houses_file.exists():
        print("Файл data/houses.json не найден")
        return

    with open(houses_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    async with async_session() as session:
        from sqlalchemy import select
        result = await session.execute(select(Building).limit(1))
        if result.scalar_one_or_none():
            print("База уже содержит дома")
            return

        for b in data.get("buildings", []):
            building = Building(
                address=b["address"],
                entrances_count=b.get("entrances_count", 1),
                floors_count=b.get("floors_count", 1)
            )
            session.add(building)
            await session.flush()

            for apt in b.get("apartments", []):
                apartment = Apartment(
                    building_id=building.id,
                    entrance=apt.get("entrance", 1),
                    floor=apt.get("floor", 1),
                    number=str(apt["number"]),
                    window_side=apt.get("window_side", "unknown")
                )
                session.add(apartment)

        await session.commit()
        print("Дома и квартиры загружены из data/houses.json")

async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await load_houses_from_file()

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
    asyncio.create_task(dp.start_polling(Bot(token=BOT_TOKEN), skip_updates=True))

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)