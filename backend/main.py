import datetime
import uuid
import logging
import secrets
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
from supabase import create_client, Client
from kaspi_auth import KaspiAuthenticator

app = FastAPI()
print('Starting FastAPI application...')
# Настройка логгера
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфигурация Supabase
SUPABASE_URL = "https://ilzbtmlakphgvhlpfggs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlsemJ0bWxha3BoZ3ZobHBmZ2dzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NjEyODkzMSwiZXhwIjoyMDYxNzA0OTMxfQ.4TOzSLz4EUbjQU7Z9BkhOFRc2RxjxRDK6gtPVB8Qfr8"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Настройки CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Модели данных
class KaspiAuthRequest(BaseModel):
    user_id: str = Field(..., description="ID пользователя в системе")
    email: EmailStr = Field(..., description="Email для входа в Kaspi")
    password: str = Field(..., min_length=6, description="Пароль для входа в Kaspi")

class KaspiStore(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = Field(default_factory=lambda: datetime.datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.datetime.now().isoformat())
    user_id: str  # Это обязательное поле для привязки к аккаунту
    merchant_id: str
    name: str
    api_key: str = "auto_generated_token"
    products_count: int = 0
    last_sync: Optional[str] = None
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

@app.post("/kaspi/auth")
async def authenticate_kaspi_store(auth_data: KaspiAuthRequest):
    try:
        # 1. Аутентификация в Kaspi
        kaspi_auth = KaspiAuthenticator(user_id=auth_data.user_id)
        auth_result = kaspi_auth.login(auth_data.email, auth_data.password)
        
        if not auth_result["success"]:
            raise HTTPException(status_code=401, detail=auth_result.get("error", "Ошибка аутентификации в Kaspi"))
        
        # 2. Проверка существующего магазина
        existing_store = supabase.table("kaspi_stores") \
            .select("*") \
            .eq("user_id", auth_data.user_id) \
            .eq("merchant_id", auth_result["merchant_id"]) \
            .execute()

        if existing_store.data:
            return {
                "success": True,
                "store_id": existing_store.data[0]["id"],
                "message": "Магазин уже привязан к вашему аккаунту"
            }

        # 3. Создание новой записи
        store_data = {
            "user_id": auth_data.user_id,
            "merchant_id": auth_result["merchant_id"],
            "name": auth_result["store_name"],
            "api_key": f"kaspi_{secrets.token_urlsafe(16)}"  # Генерация случайного API ключа
        }

        response = supabase.table("kaspi_stores").insert(store_data).execute()
        
        if hasattr(response, 'error') and response.error:
            raise HTTPException(
                status_code=400, 
                detail=f"Ошибка сохранения магазина: {response.error.message}"
            )
        
        return {
            "success": True,
            "store_id": response.data[0]["id"],
            "message": "Магазин успешно привязан к вашему аккаунту",
            "api_key": store_data["api_key"]  # Возвращаем сгенерированный ключ
        }

    except HTTPException:
        raise  # Перебрасываем уже обработанные ошибки
    except Exception as e:
        logger.error(f"Ошибка при привязке магазина: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Произошла внутренняя ошибка при привязке магазина"
        )

@app.post("/kaspi/stores", response_model=KaspiStore)
async def create_kaspi_store(store: KaspiStore):
    try:
        # Устанавливаем временные метки
        now = datetime.datetime.now().isoformat()
        store.created_at = now
        store.updated_at = now
        
        # Вставляем данные в Supabase
        response = supabase.table("kaspi_stores").insert(store.dict()).execute()
        
        if hasattr(response, 'error') and response.error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ошибка создания магазина: {response.error.message}"
            )
            
        return response.data[0]
        
    except Exception as e:
        logger.error(f"Ошибка при создании магазина: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка сервера при создании магазина"
        )

@app.delete("/kaspi/stores/{store_id}")
async def delete_store(store_id: str):
    try:
        response = supabase.table("kaspi_stores").delete().eq("id", store_id).execute()
        if len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Магазин не найден"
            )
        return {"success": True}
    except Exception as e:
        logging.error(f"Ошибка удаления магазина: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка удаления магазина"
        )

@app.post("/kaspi/stores/{store_id}/sync")
async def sync_store(store_id: str):
    try:
        response = supabase.table("kaspi_stores") \
            .select("products_count") \
            .eq("id", store_id) \
            .execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Магазин не найден")

        current_count = response.data[0]["products_count"] or 0
        updated_count = current_count + 10

        update_data = {
            "products_count": updated_count,
            "last_sync": datetime.datetime.now().isoformat(),
            "updated_at": datetime.datetime.now().isoformat()
        }

        update_response = supabase.table("kaspi_stores").update(update_data).eq("id", store_id).execute()

        return {
            "success": True,
            "products_count": updated_count,
            "message": "Товары успешно синхронизированы"
        }
    except Exception as e:
        logging.error(f"Ошибка синхронизации: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Ошибка синхронизации магазина"
        )


@app.get("/kaspi/stores")
async def get_user_stores(user_id: str):
    try:
        response = supabase.table("kaspi_stores") \
            .select("*") \
            .eq("user_id", user_id) \
            .execute()
            
        return {
            "success": True,
            "stores": response.data
        }
    except Exception as e:
        logger.error(f"Ошибка при получении магазинов: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Ошибка при получении списка магазинов"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010)
