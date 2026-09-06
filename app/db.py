from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import DATABASE_URL

# Если используем SQLite, нужен aiosqlite
if DATABASE_URL.startswith("sqlite"):
    engine = create_async_engine(DATABASE_URL, echo=False)
else:
    engine = create_async_engine(DATABASE_URL, echo=False, pool_size=10, max_overflow=20)

Base = declarative_base()
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with async_session() as session:
        yield session