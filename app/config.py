import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")

def parse_ids(env_value):
    if not env_value or env_value.strip() == "":
        return []
    return [int(x.strip()) for x in env_value.split(",") if x.strip()]

ADMIN_IDS = parse_ids(os.getenv("ADMIN_IDS", ""))
WORKER_IDS = parse_ids(os.getenv("WORKER_IDS", ""))
MINI_APP_URL = os.getenv("MINI_APP_URL", "https://example.com")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
