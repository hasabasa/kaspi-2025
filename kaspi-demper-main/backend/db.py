import asyncpg
import asyncio
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

_pool: Optional[asyncpg.Pool] = None
_lock = asyncio.Lock()


async def create_pool() -> asyncpg.Pool:
    """Возвращает пул соединений (синглтон). Пересоздаёт, если закрыт."""
    global _pool

    async with _lock:  # защищаем от одновременного вызова
        if _pool is None or _pool._closed:
            _pool = await asyncpg.create_pool(
                user=os.getenv("DB_USER", "demper_user"),
                password=os.getenv("DB_PASSWORD", "tUrGenTLaMySHWARestOrecKERguEb"),
                database=os.getenv("DB_NAME", "demper"),
                host=os.getenv("DB_HOST", "95.179.187.42"),
                port=int(os.getenv("DB_PORT", "6432")),
                min_size=10,
                max_size=50,
                max_queries=50000,
                timeout=30,
            )
    return _pool


async def close_pool():
    """Закрыть пул соединений (на shutdown)."""
    global _pool
    if _pool and not _pool._closed:
        await _pool.close()
        _pool = None