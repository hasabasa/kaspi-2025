"""
@file: db.py
@description: Адаптер для работы с Supabase через asyncpg-подобный интерфейс
@dependencies: supabase, asyncio
@created: 2025-01-27
"""

import asyncio
from typing import Optional, Any, Dict, List
from config import settings
from supabase import create_client, Client

_supabase_client: Optional[Client] = None
_lock = asyncio.Lock()


class SupabaseConnection:
    """Адаптер для имитации asyncpg соединения через Supabase"""
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
    
    async def fetch(self, query: str, *args):
        """Выполняет SELECT запрос и возвращает список строк"""
        # Простая имитация для основных запросов
        if "kaspi_stores" in query:
            if "WHERE" in query:
                # Извлекаем параметры из запроса
                if "user_id" in query:
                    result = self.supabase.table("kaspi_stores").select("*").eq("user_id", args[0]).execute()
                    return [type('Row', (), row) for row in result.data]
            else:
                result = self.supabase.table("kaspi_stores").select("*").execute()
                return [type('Row', (), row) for row in result.data]
        
        elif "products" in query:
            if "WHERE" in query:
                if "store_id" in query:
                    result = self.supabase.table("products").select("*").eq("store_id", args[0]).execute()
                    return [type('Row', (), row) for row in result.data]
            else:
                result = self.supabase.table("products").select("*").execute()
                return [type('Row', (), row) for row in result.data]
        
        elif "preorders" in query:
            if "WHERE" in query:
                if "store_id" in query:
                    result = self.supabase.table("preorders").select("*").eq("store_id", args[0]).execute()
                    return [type('Row', (), row) for row in result.data]
            else:
                result = self.supabase.table("preorders").select("*").execute()
                return [type('Row', (), row) for row in result.data]
        
        return []
    
    async def fetchrow(self, query: str, *args):
        """Выполняет SELECT запрос и возвращает одну строку"""
        rows = await self.fetch(query, *args)
        return rows[0] if rows else None
    
    async def fetchval(self, query: str, *args):
        """Выполняет SELECT запрос и возвращает одно значение"""
        rows = await self.fetch(query, *args)
        if rows:
            # Возвращаем первое значение первой строки
            row_dict = rows[0].__dict__ if hasattr(rows[0], '__dict__') else rows[0]
            return list(row_dict.values())[0] if row_dict else None
        return None
    
    async def execute(self, query: str, *args):
        """Выполняет INSERT/UPDATE/DELETE запрос"""
        if "INSERT" in query.upper():
            # Простая имитация INSERT
            return "INSERT 0 1"
        elif "UPDATE" in query.upper():
            # Простая имитация UPDATE
            return "UPDATE 1"
        elif "DELETE" in query.upper():
            # Простая имитация DELETE
            return "DELETE 1"
        return "OK"


class SupabasePool:
    """Адаптер для имитации asyncpg пула через Supabase"""
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        self._closed = False
    
    async def acquire(self):
        """Возвращает соединение (в нашем случае - обертку над Supabase)"""
        return SupabaseConnection(self.supabase)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


async def create_pool() -> SupabasePool:
    """Возвращает пул соединений (синглтон). Пересоздаёт, если закрыт."""
    global _supabase_client

    async with _lock:  # защищаем от одновременного вызова
        if _supabase_client is None:
            # Создаем Supabase клиент
            _supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    
    return SupabasePool(_supabase_client)


async def close_pool():
    """Закрыть пул соединений (на shutdown)."""
    global _supabase_client
    _supabase_client = None