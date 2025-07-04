from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from bot.config import DB_POSTGRES  # Импортируем DATABASE_URL из bot/config.py

# URL для подключения к базе данных (асинхронный драйвер asyncpg)
DATABASE_URL_ASYNC = DB_POSTGRES.replace("postgresql://", "postgresql+asyncpg://")

# Создаём асинхронный движок SQLAlchemy
engine = create_async_engine(DATABASE_URL_ASYNC, echo=True)

# Создаём фабрику асинхронных сессий
async_session = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Функция для получения асинхронной сессии базы данных
async def get_db():
    async with async_session() as session:
        yield session