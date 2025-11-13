from fastapi import APIRouter, HTTPException, status
from core.logger import logger
from api_parser import SessionManager
from utils import has_active_subscription, has_existing_store
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import uuid4
from db import create_pool

router = APIRouter(prefix="/kaspi/stores", tags=["stores"])

class KaspiStore(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    user_id: str
    merchant_id: str
    name: str
    api_key: str = "auto_generated_token"
    products_count: int = 0
    last_sync: str | None = None
    is_active: bool = True

    class Config:
        json_schema_extra = {
            "example": {
                "id": "38269a19-dfc3-40c5-a7b7-e28489ade1b6",
                "created_at": "2025-06-24T19:39:24.963775+00:00",
                "updated_at": "2025-06-24T19:39:24.963775+00:00",
                "user_id": "7af6685a-812f-4525-ba67-6157097f43c3",
                "merchant_id": "kaspi_1750793959893",
                "name": "Магазин kaspidemping",
                "api_key": "auto_generated_token",
                "products_count": 0,
                "last_sync": "2025-06-24T19:39:19.893+00:00",
                "is_active": True
            }
        }


@router.post("/", response_model=KaspiStore)
async def create_kaspi_store(store: KaspiStore):
    try:
        if not await has_active_subscription(store.user_id):
            logger.warning(f"User {store.user_id} attempted to create store without active subscription")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Active subscription required to add a Kaspi store"
            )
        
        # check if user already has a store, but allow replacement
        pool = await create_pool()
        async with pool.acquire() as conn:
            existing = await conn.fetchrow(
                """
                SELECT id, merchant_id, name
                FROM kaspi_stores
                WHERE user_id = $1
                LIMIT 1
                """,
                store.user_id
            )

        now = datetime.now().isoformat()
        
        if existing:
            # update existing store with new data
            async with pool.acquire() as conn:
                result = await conn.fetchrow(
                    """
                    UPDATE kaspi_stores 
                    SET merchant_id = $1, name = $2, api_key = $3, updated_at = $4, last_sync = NULL
                    WHERE user_id = $5
                    RETURNING *
                    """,
                    store.merchant_id, store.name, store.api_key, now, store.user_id
                )
            
            logger.info(f"Store updated for user {store.user_id}: {result['id']}")
            return dict(result)
        else:
            # create new store
            store.created_at = now
            store.updated_at = now

            async with pool.acquire() as conn:
                result = await conn.fetchrow(
                    """
                    INSERT INTO kaspi_stores (id, created_at, updated_at, user_id, merchant_id, name, api_key, products_count, last_sync, is_active)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                    RETURNING *
                    """,
                    store.id, store.created_at, store.updated_at, store.user_id, 
                    store.merchant_id, store.name, store.api_key, store.products_count, 
                    store.last_sync, store.is_active
                )

            if not result:
                logger.error("Ошибка создания магазина: не удалось получить результат")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ошибка создания магазина: не удалось получить результат"
                )

            logger.info(f"Создан магазин {store.id} для пользователя {store.user_id}")
            return dict(result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при создании магазина: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка сервера при создании магазина"
        )

@router.get("/{store_id}/session")
async def check_store_session(store_id: str):
    try:
        pool = await create_pool()
        async with pool.acquire() as conn:
            store = await conn.fetchrow(
                """
                SELECT id FROM kaspi_stores WHERE id = $1
                """,
                store_id
            )
            
            if not store:
                logger.warning(f"Store {store_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Store not found"
                )
        
        session_manager = SessionManager(shop_uid=store_id)
        is_valid = await session_manager.load()
        if not is_valid:
            logger.warning(f"Сессия для магазина {store_id} недействительна или истекла")
            return {
                "success": False,
                "is_valid": False,
                "message": "Сессия недействительна или истекла. Пожалуйста, переавторизуйте магазин."
            }

        logger.info(f"Сессия для магазина {store_id} действительна")
        return {
            "success": True,
            "is_valid": True,
            "message": "Сессия действительна"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при проверке сессии магазина {store_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при проверке сессии магазина: {str(e)}"
        )
        
@router.delete("/{store_id}")
async def delete_kaspi_store(store_id: str, user_id: str):
    try:
        logger.info(f"Attempting to delete store {store_id} for user {user_id}")
        
        pool = await create_pool()
        async with pool.acquire() as conn:
            store = await conn.fetchrow(
                """
                SELECT id, user_id, name FROM kaspi_stores 
                WHERE id = $1
                """,
                store_id
            )
            
            if not store:
                logger.warning(f"Store {store_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Store not found"
                )
            
            
            result = await conn.execute(
                """
                DELETE FROM kaspi_stores 
                WHERE id = $1
                """,
                store_id
            )
            
            if result == "DELETE 1":
                logger.info(f"Successfully deleted store {store_id} for user {user_id}")
                return {
                    "success": True,
                    "message": f"Store '{store['name']}' successfully deleted"
                }
            else:
                logger.error(f"Failed to delete store {store_id}: unexpected result {result}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to delete store"
                )
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting store {store_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting store: {str(e)}"
        )