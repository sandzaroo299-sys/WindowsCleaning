import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(",")))
WORKER_IDS = list(map(int, os.getenv("WORKER_IDS", "").split(",")))
MINI_APP_URL = os.getenv("MINI_APP_URL", "https://example.com")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")

# Для теста можно использовать SQLite, но в проде — PostgreSQL
# Например, если DATABASE_URL не задан, берём sqlite