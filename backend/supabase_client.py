from supabase import create_client, Client
import os
from typing import List, Dict, Any

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

class SupabaseStoreManager:
    @staticmethod
    async def get_user_stores(user_id: str) -> List[Dict[str, Any]]:
        response = supabase.table("kaspi_stores").select("*").eq("user_id", user_id).execute()
        return response.data

    @staticmethod
    async def add_store(store_data: Dict[str, Any]) -> Dict[str, Any]:
        response = supabase.table("kaspi_stores").insert(store_data).execute()
        return response.data[0] if response.data else None

    @staticmethod
    async def delete_store(store_id: str) -> bool:
        response = supabase.table("kaspi_stores").delete().eq("id", store_id).execute()
        return len(response.data) > 0

    @staticmethod
    async def update_store(store_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        response = supabase.table("kaspi_stores").update(update_data).eq("id", store_id).execute()
        return response.data[0] if response.data else None