from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel, Field
from uuid import UUID
from typing import List, Optional
from datetime import datetime
from db import create_pool
import logging
import re
import time
from enum import Enum
from utils import sanitize_name_filter, validate_store_id, validate_product_ids

router = APIRouter(prefix="/products", tags=["products"])

logger = logging.getLogger(__name__)

class OrderDirection(str, Enum):
    ASC = "ASC"
    DESC = "DESC"

class BatchProductRequest(BaseModel):
    store_id: UUID = Field(..., description="ID of the store")
    product_ids: List[str] = Field(..., description="List of kaspi_product_id values to enable/disable")

class ProductResponse(BaseModel):
    id: UUID
    store_id: UUID
    kaspi_product_id: str
    name: str
    price: float
    image_url: Optional[str]
    category: Optional[str]
    bot_active: bool
    min_profit: Optional[float]
    max_profit: Optional[float]
    external_kaspi_id: Optional[str]
    kaspi_sku: Optional[str]
    strategy: Optional[str]

    class Config:
        json_schema_extra = {
            "example": {
                "id": "38269a19-dfc3-40c5-a7b7-e28489ade1b6",
                "store_id": "7af6685a-812f-4525-ba67-6157097f43c3",
                "kaspi_product_id": "12345",
                "name": "Smartphone Pro",
                "price": 999.00,
                "image_url": "https://kaspi.kz/img/phone.jpg",
                "category": "Electronics",
                "bot_active": True,
                "min_profit": 100.00,
                "max_profit": 500.00,
                "external_kaspi_id": "67890",
                "kaspi_sku": "SKU12345",
                "strategy": "competitive"
            }
        }

class BatchResponse(BaseModel):
    success: bool
    updated_count: int
    failed_ids: List[str]
    message: str

class PaginatedProductResponse(BaseModel):
    products: List[ProductResponse]
    total: int
    page: int
    page_size: int

    

@router.post("/batch_enable", response_model=BatchResponse)
async def batch_enable_products(request: BatchProductRequest):
    start_time = time.time()
    try:
        if not await validate_store_id(request.store_id):
            logger.warning(f"Store {request.store_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Store {request.store_id} not found"
            )
        
        valid_ids, failed_ids = await validate_product_ids(request.store_id, request.product_ids)

        if not valid_ids:
            logger.warning(f"No valid kaspi_product_id values found for store {request.store_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No valid product IDs found for the given store"
            )

        pool = await create_pool()
        async with pool.acquire() as conn:
            query = f"""
                UPDATE products 
                SET bot_active = TRUE 
                WHERE kaspi_product_id = ANY($1) AND store_id = $2
            """
            await conn.execute(query, valid_ids, str(request.store_id))

        updated_count = len(valid_ids)
        logger.info(f"Enabled bot_active for {updated_count} products in store {request.store_id}, took {time.time() - start_time:.2f} seconds")
        return {
            "success": True,
            "updated_count": updated_count,
            "failed_ids": failed_ids,
            "message": f"Успешно включено продуктов: {updated_count}"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch_enable_products: {str(e)}, took {time.time() - start_time:.2f} seconds")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error during batch enable: {str(e)}"
        )

@router.post("/batch_disable", response_model=BatchResponse)
async def batch_disable_products(request: BatchProductRequest):
    start_time = time.time()
    try:
        if not await validate_store_id(request.store_id):
            logger.warning(f"Store {request.store_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Store {request.store_id} not found"
            )

        valid_ids, failed_ids = await validate_product_ids(request.store_id, request.product_ids)

        if not valid_ids:
            logger.warning(f"No valid kaspi_product_id values found for store {request.store_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No valid product IDs found for the given store"
            )

        pool = await create_pool()
        async with pool.acquire() as conn:
            query = f"""
                UPDATE products 
                SET bot_active = FALSE 
                WHERE kaspi_product_id = ANY($1) AND store_id = $2
            """
            await conn.execute(query, valid_ids, str(request.store_id))

        updated_count = len(valid_ids)
        logger.info(f"Disabled bot_active for {updated_count} products in store {request.store_id}, took {time.time() - start_time:.2f} seconds")
        return {
            "success": True,
            "updated_count": updated_count,
            "failed_ids": failed_ids,
            "message": f"Успешно отключено продуктов: {updated_count}"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch_disable_products: {str(e)}, took {time.time() - start_time:.2f} seconds")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error during batch disable: {str(e)}"
        )

@router.get("/", response_model=PaginatedProductResponse)
async def list_products(
    store_id: UUID = Query(..., description="ID of the store"),
    name: Optional[str] = Query(None, description="Filter by product name (min 3 characters)"),
    active: Optional[bool] = Query(None, description="Filter by bot_active status"),
    order_by: str = Query("id", description="Order by field: id, price, bot_active", regex="^(id|price|bot_active)$"),
    order_direction: OrderDirection = Query(OrderDirection.ASC),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Number of products per page")
):
    start_time = time.time()
    try:
        if not await validate_store_id(store_id):
            logger.warning(f"Store {store_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Store {store_id} not found"
            )

        pool = await create_pool()
        
        base_query = """
            SELECT id, store_id, kaspi_product_id, name, price, image_url, 
                   category, bot_active, min_profit, max_profit, 
                   external_kaspi_id, kaspi_sku, strategy
            FROM products 
            WHERE store_id = $1
        """
        params = [str(store_id)]
        param_count = 1

        if name:
            sanitized_name = sanitize_name_filter(name)
            param_count += 1
            base_query += f" AND name ILIKE ${param_count}"
            params.append(f"%{sanitized_name}%")

        if active is not None:
            param_count += 1
            base_query += f" AND bot_active = ${param_count}"
            params.append(active)
            
        normalized_direction = order_direction.value

        if order_by == "id":
            base_query += f" ORDER BY id {normalized_direction}"
        elif order_by == "price":
            base_query += f" ORDER BY price {normalized_direction}, id ASC"
        elif order_by == "bot_active":
            base_query += f" ORDER BY bot_active {normalized_direction}, id ASC"
        else:
            base_query += " ORDER BY id ASC"

        offset = (page - 1) * page_size
        base_query += f" LIMIT ${param_count + 1} OFFSET ${param_count + 2}"
        params.extend([page_size, offset])

        async with pool.acquire() as conn:
            products = await conn.fetch(base_query, *params)

        count_query = """
            SELECT COUNT(*) as total
            FROM products 
            WHERE store_id = $1
        """
        count_params = [str(store_id)]
        count_param_count = 1

        if name:
            count_param_count += 1
            count_query += f" AND name ILIKE ${count_param_count}"
            count_params.append(f"%{sanitized_name}%")

        if active is not None:
            count_param_count += 1
            count_query += f" AND bot_active = ${count_param_count}"
            count_params.append(active)

        async with pool.acquire() as conn:
            count_result = await conn.fetchrow(count_query, *count_params)
            total = count_result['total'] if count_result else 0

        products_data = [dict(product) for product in products]

        return {
            "products": products_data,
            "total": total,
            "page": page,
            "page_size": page_size
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in list_products: {str(e)}, took {time.time() - start_time:.2f} seconds")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error during product retrieval: {str(e)}"
        )

@router.get("/store_stats", response_model=dict)
async def get_store_stats(store_id: UUID = Query(..., description="ID of the store")):
    start_time = time.time()
    try:
        if not await validate_store_id(store_id):
            logger.warning(f"Store {store_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Store {store_id} not found"
            )

        pool = await create_pool()
        
        stats_query = """
            SELECT 
                COUNT(*) as total_products,
                COUNT(CASE WHEN bot_active = TRUE THEN 1 END) as active_bots,
                COUNT(CASE WHEN strategy IS NOT NULL AND strategy != '' THEN 1 END) as with_strategy,
                COUNT(CASE WHEN min_profit IS NOT NULL OR max_profit IS NOT NULL THEN 1 END) as with_limits,
                AVG(price) as avg_price
            FROM products 
            WHERE store_id = $1
        """
        
        async with pool.acquire() as conn:
            stats_result = await conn.fetchrow(stats_query, str(store_id))
            
            if not stats_result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No products found for the store"
                )

        stats = {
            "total_products": stats_result['total_products'],
            "active_bots": stats_result['active_bots'],
            "with_strategy": stats_result['with_strategy'],
            "with_limits": stats_result['with_limits'],
            "avg_price": float(stats_result['avg_price']) if stats_result['avg_price'] else 0
        }

        logger.info(f"Fetched store stats for store {store_id}, took {time.time() - start_time:.2f} seconds")
        return stats

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_store_stats: {str(e)}, took {time.time() - start_time:.2f} seconds")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error during stats retrieval: {str(e)}"
        )

@router.put("/{product_id}/strategy", response_model=dict)
async def update_product_strategy(
    product_id: str,
    store_id: UUID = Query(..., description="ID of the store"),
    strategy: Optional[str] = Query(None, description="Pricing strategy"),
    min_profit: Optional[float] = Query(None, description="Minimum profit/price"),
    max_profit: Optional[float] = Query(None, description="Maximum profit/price")
):
    start_time = time.time()
    try:
        if not await validate_store_id(store_id):
            logger.warning(f"Store {store_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Магазин {store_id} не найден"
            )

        pool = await create_pool()
        
        update_fields = []
        params = [str(store_id), product_id]
        param_count = 2
        
        if strategy is not None:
            param_count += 1
            update_fields.append(f"strategy = ${param_count}")
            params.append(strategy)
            
        if min_profit is not None:
            param_count += 1
            update_fields.append(f"min_profit = ${param_count}")
            params.append(min_profit)
            
        if max_profit is not None:
            param_count += 1
            update_fields.append(f"max_profit = ${param_count}")
            params.append(max_profit)
        
        if not update_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Не выбрано ни одного поля для обновления"
            )
        
        param_count += 1
        update_fields.append(f"updated_at = ${param_count}")
        params.append(datetime.now())
        
        update_query = f"""
            UPDATE products 
            SET {', '.join(update_fields)}
            WHERE id = $2 AND store_id = $1
        """
        
        async with pool.acquire() as conn:
            result = await conn.execute(update_query, *params)
            
            if result == 'UPDATE 0':
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Продукт не найден в указанном магазине"
                )

        logger.info(f"Updated product strategy for product {product_id} in store {store_id}, took {time.time() - start_time:.2f} seconds")
        return {
            "success": True,
            "message": "Стратегия успешно применена к выбранным товарам!",
            "updated_fields": [field.split(' = ')[0] for field in update_fields if not field.startswith('updated_at')]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in update_product_strategy: {str(e)}, took {time.time() - start_time:.2f} seconds")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error during strategy update: {str(e)}"
        )