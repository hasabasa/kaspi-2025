from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
import asyncio
import psutil
import os
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

from db import create_pool
from utils import get_supabase_client

router = APIRouter(prefix="/admin", tags=["admin"])

async def verify_admin_user(user_id: str) -> bool:
    try:
        supabase = get_supabase_client()
        
        result = supabase.table("user_roles").select("role").eq("user_id", user_id).eq("role", "admin").execute()
        
        return len(result.data) > 0
    except Exception:
        return False

async def verify_admin(admin_user_id: str):
    if not admin_user_id:
        raise HTTPException(status_code=401, detail="Admin user ID required")
    
    if not await verify_admin_user(admin_user_id):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return admin_user_id

class SystemStatus(BaseModel):
    status: str
    timestamp: datetime
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    disk_usage: Optional[float] = None
    processes: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class BackendStats(BaseModel):
    stores: int
    products: int
    preorders: int
    active_stores: int
    active_bots: int
    recent_products: int
    recent_preorders: int
    preorder_statuses: Dict[str, int]
    stores_with_sync: int
    total_products_value: float
    last_updated: datetime

class ServiceHealth(BaseModel):
    fastapi_status: str
    demper_status: str
    timestamp: datetime
    error: Optional[str] = None

class DatabaseStats(BaseModel):
    status: str
    uptime_hours: Optional[float] = None
    table_sizes: Dict[str, int]
    last_checked: datetime
    error: Optional[str] = None

class ProcessStats(BaseModel):
    name: str
    pid: int
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    status: str
    create_time: datetime
    uptime_seconds: float

async def get_system_status() -> SystemStatus:
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        processes = {}
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                if proc.info['name'] in ['python', 'demper', 'price-worker']:
                    processes[proc.info['name']] = {
                        'pid': proc.info['pid'],
                        'cpu_percent': proc.info['cpu_percent'],
                        'memory_percent': proc.info['memory_percent']
                    }
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return SystemStatus(
            status="healthy",
            timestamp=datetime.utcnow(),
            cpu_usage=cpu_percent,
            memory_usage=memory.percent,
            disk_usage=disk.percent,
            processes=processes
        )
    except Exception as e:
        return SystemStatus(
            status="error",
            timestamp=datetime.utcnow(),
            error=str(e)
        )

@router.get("/system/status", response_model=SystemStatus)
async def get_system_health(admin_user_id: str):
    await verify_admin(admin_user_id)
    return await get_system_status()

@router.get("/system/stats", response_model=BackendStats)
async def get_backend_stats(admin_user_id: str):
    await verify_admin(admin_user_id)
    try:
        pool = await create_pool()
        
        async with pool.acquire() as conn:
            stores_count = await conn.fetchval("SELECT COUNT(*) FROM kaspi_stores")
            products_count = await conn.fetchval("SELECT COUNT(*) FROM products")
            preorders_count = await conn.fetchval("SELECT COUNT(*) FROM preorders")
            
            active_stores = await conn.fetchval(
                "SELECT COUNT(*) FROM kaspi_stores WHERE is_active = true"
            )
            
            active_bots = await conn.fetchval(
                "SELECT COUNT(*) FROM products WHERE bot_active = true"
            )
            
            yesterday = datetime.utcnow() - timedelta(days=1)
            recent_products = await conn.fetchval(
                "SELECT COUNT(*) FROM products WHERE created_at >= $1",
                yesterday
            )
            
            recent_preorders = await conn.fetchval(
                "SELECT COUNT(*) FROM preorders WHERE created_at >= $1",
                yesterday
            )
            
            preorder_statuses_result = await conn.fetch(
                """
                SELECT status, COUNT(*) as count 
                FROM preorders 
                GROUP BY status
                """
            )
            status_distribution = {row['status']: row['count'] for row in preorder_statuses_result}
            
            stores_with_sync = await conn.fetchval(
                "SELECT COUNT(*) FROM kaspi_stores WHERE last_sync IS NOT NULL"
            )
            
            total_value = await conn.fetchval(
                "SELECT COALESCE(SUM(price), 0) FROM products"
            )
            
        return BackendStats(
            stores=stores_count or 0,
            products=products_count or 0,
            preorders=preorders_count or 0,
            active_stores=active_stores or 0,
            active_bots=active_bots or 0,
            recent_products=recent_products or 0,
            recent_preorders=recent_preorders or 0,
            preorder_statuses=status_distribution,
            stores_with_sync=stores_with_sync or 0,
            total_products_value=float(total_value or 0),
            last_updated=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting backend stats: {str(e)}")

@router.get("/system/health", response_model=ServiceHealth)
async def get_service_health(admin_user_id: str):
    await verify_admin(admin_user_id)
    try:
        health_status = ServiceHealth(
            fastapi_status="healthy",
            demper_status="healthy",
            timestamp=datetime.utcnow()
        )
        
        try:
            pool = await create_pool()
            async with pool.acquire() as conn:
                result = await conn.fetchval("SELECT 1")
            if not result:
                health_status.fastapi_status = "unhealthy"
        except Exception:
            health_status.fastapi_status = "unhealthy"
        
        try:
            demper_running = False
            for proc in psutil.process_iter(['name']):
                if 'demper' in proc.info['name'].lower() or 'price-worker' in proc.info['name'].lower():
                    demper_running = True
                    break
            
            if not demper_running:
                health_status.demper_status = "unhealthy"
        except Exception:
            health_status.demper_status = "unknown"
        
        return health_status
        
    except Exception as e:
        return ServiceHealth(
            fastapi_status="error",
            demper_status="error",
            timestamp=datetime.utcnow(),
            error=str(e)
        )

@router.get("/system/database", response_model=DatabaseStats)
async def get_database_stats(admin_user_id: str):
    await verify_admin(admin_user_id)
    try:
        pool = await create_pool()
        
        async with pool.acquire() as conn:
            result = await conn.fetchval("SELECT 1")
            connection_status = "connected" if result else "disconnected"
            
            table_sizes = {}
            for table_name in ['kaspi_stores', 'products', 'preorders']:
                try:
                    count = await conn.fetchval(f"SELECT COUNT(*) FROM {table_name}")
                    table_sizes[table_name] = count or 0
                except Exception:
                    table_sizes[table_name] = 0
            
            uptime_result = await conn.fetchval(
                "SELECT EXTRACT(EPOCH FROM (now() - pg_postmaster_start_time())) / 3600"
            )
            uptime_hours = uptime_result or 0
            
        return DatabaseStats(
            status=connection_status,
            uptime_hours=float(uptime_hours),
            table_sizes=table_sizes,
            last_checked=datetime.utcnow()
        )
        
    except Exception as e:
        return DatabaseStats(
            status="error",
            error=str(e),
            last_checked=datetime.utcnow()
        )

@router.get("/system/processes", response_model=List[ProcessStats])
async def get_process_stats(admin_user_id: str):
    await verify_admin(admin_user_id)
    try:
        processes = []
        
        target_processes = ['python', 'demper', 'price-worker', 'uvicorn', 'fastapi']
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'create_time']):
            try:
                proc_info = proc.info
                if any(target in proc_info['name'].lower() for target in target_processes):
                    try:
                        proc_obj = psutil.Process(proc_info['pid'])
                        memory_info = proc_obj.memory_info()
                        
                        processes.append(ProcessStats(
                            name=proc_info['name'],
                            pid=proc_info['pid'],
                            cpu_percent=proc_info['cpu_percent'] or 0,
                            memory_percent=proc_info['memory_percent'] or 0,
                            memory_mb=memory_info.rss / 1024 / 1024,
                            status=proc_obj.status(),
                            create_time=datetime.fromtimestamp(proc_info['create_time']),
                            uptime_seconds=(datetime.now() - datetime.fromtimestamp(proc_info['create_time'])).total_seconds()
                        ))
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return processes
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting process stats: {str(e)}")

@router.post("/system/restart")
async def restart_service(service: str, admin_user_id: str):
    await verify_admin(admin_user_id)
    return {"message": f"Restart command sent for {service}", "status": "pending"}