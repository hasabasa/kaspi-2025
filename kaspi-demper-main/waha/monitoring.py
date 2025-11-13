# monitoring.py
"""
Мониторинг и метрики для WAHA модуля
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from uuid import UUID
import json

from .config import get_config
from .utils import get_metrics_collector, get_error_handler
from .database import WAHA_Database

logger = logging.getLogger(__name__)


class WAHAMonitor:
    """Монитор WAHA модуля"""
    
    def __init__(self, db: WAHA_Database):
        self.config = get_config()
        self.db = db
        self.metrics_collector = get_metrics_collector()
        self.error_handler = get_error_handler()
        self._monitoring_task: Optional[asyncio.Task] = None
        self._is_running = False
    
    async def start_monitoring(self):
        """Запуск мониторинга"""
        if self._is_running:
            return
        
        self._is_running = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("WAHA мониторинг запущен")
    
    async def stop_monitoring(self):
        """Остановка мониторинга"""
        if not self._is_running:
            return
        
        self._is_running = False
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("WAHA мониторинг остановлен")
    
    async def _monitoring_loop(self):
        """Основной цикл мониторинга"""
        check_interval = self.config.get("session_check_interval_minutes", 5) * 60
        
        while self._is_running:
            try:
                await self._check_sessions_health()
                await self._update_metrics()
                await self._check_error_thresholds()
                
                await asyncio.sleep(check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Ошибка в цикле мониторинга: {e}")
                await asyncio.sleep(60)  # Ждем минуту при ошибке
    
    async def _check_sessions_health(self):
        """Проверка здоровья сессий"""
        try:
            # Получаем все активные сессии
            enabled_stores = await self.db.get_enabled_stores()
            
            active_sessions = 0
            failed_sessions = 0
            
            for store_id in enabled_stores:
                session_info = await self.db.get_session_info(store_id)
                
                if session_info:
                    if session_info.is_connected:
                        active_sessions += 1
                    else:
                        failed_sessions += 1
                        
                        # Логируем проблему с сессией
                        self.error_handler.log_error(
                            "session_disconnected",
                            f"Сессия магазина {store_id} отключена",
                            {"store_id": str(store_id), "status": session_info.status}
                        )
            
            # Обновляем метрики
            await self.metrics_collector.set("sessions_active", active_sessions)
            await self.metrics_collector.set("sessions_failed", failed_sessions)
            
        except Exception as e:
            logger.error(f"Ошибка проверки здоровья сессий: {e}")
    
    async def _update_metrics(self):
        """Обновление метрик"""
        try:
            # Получаем статистику сообщений за последние 24 часа
            enabled_stores = await self.db.get_enabled_stores()
            
            total_sent = 0
            total_failed = 0
            total_delivered = 0
            
            for store_id in enabled_stores:
                try:
                    # Получаем статистику для магазина
                    async with self.db.pool.acquire() as conn:
                        stats = await conn.fetchrow("""
                            SELECT 
                                COUNT(*) as total,
                                COUNT(CASE WHEN status = 'sent' THEN 1 END) as sent,
                                COUNT(CASE WHEN status = 'delivered' THEN 1 END) as delivered,
                                COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed
                            FROM whatsapp_messages_log
                            WHERE store_id = $1 AND sent_at >= NOW() - INTERVAL '24 hours'
                        """, store_id)
                        
                        if stats:
                            total_sent += stats['sent'] or 0
                            total_failed += stats['failed'] or 0
                            total_delivered += stats['delivered'] or 0
                            
                except Exception as e:
                    logger.error(f"Ошибка получения статистики для магазина {store_id}: {e}")
            
            # Обновляем метрики
            await self.metrics_collector.set("messages_sent_24h", total_sent)
            await self.metrics_collector.set("messages_failed_24h", total_failed)
            await self.metrics_collector.set("messages_delivered_24h", total_delivered)
            
        except Exception as e:
            logger.error(f"Ошибка обновления метрик: {e}")
    
    async def _check_error_thresholds(self):
        """Проверка порогов ошибок"""
        try:
            error_stats = self.error_handler.get_error_stats()
            
            for error_type, count in error_stats["error_counts"].items():
                threshold = self.config.get("admin_notification_threshold", 10)
                
                if count >= threshold:
                    logger.critical(f"Превышен порог ошибок для {error_type}: {count}")
                    
                    # Здесь можно добавить отправку уведомлений администратору
                    # например, через email, Slack, Telegram и т.д.
                    
        except Exception as e:
            logger.error(f"Ошибка проверки порогов ошибок: {e}")
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Получение статуса здоровья системы"""
        try:
            # Получаем основные метрики
            metrics = await self.metrics_collector.get_metrics()
            error_stats = self.error_handler.get_error_stats()
            
            # Проверяем доступность WAHA сервера
            waha_server_status = await self._check_waha_server()
            
            # Получаем статистику сессий
            enabled_stores = await self.db.get_enabled_stores()
            active_sessions = 0
            
            for store_id in enabled_stores:
                session_info = await self.db.get_session_info(store_id)
                if session_info and session_info.is_connected:
                    active_sessions += 1
            
            return {
                "status": "healthy" if waha_server_status else "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "waha_server": waha_server_status,
                "active_sessions": active_sessions,
                "total_stores": len(enabled_stores),
                "metrics": metrics,
                "error_stats": error_stats,
                "monitoring_active": self._is_running
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения статуса здоровья: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _check_waha_server(self) -> bool:
        """Проверка доступности WAHA сервера"""
        try:
            import aiohttp
            
            waha_url = self.config.get("waha_server_url", "http://localhost:3000")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{waha_url}/api/health", timeout=5) as response:
                    return response.status == 200
                    
        except Exception as e:
            logger.error(f"Ошибка проверки WAHA сервера: {e}")
            return False
    
    async def get_detailed_metrics(self, store_id: Optional[UUID] = None, days: int = 7) -> Dict[str, Any]:
        """Получение детальных метрик"""
        try:
            if store_id:
                # Метрики для конкретного магазина
                return await self._get_store_metrics(store_id, days)
            else:
                # Общие метрики
                return await self._get_global_metrics(days)
                
        except Exception as e:
            logger.error(f"Ошибка получения детальных метрик: {e}")
            return {"error": str(e)}
    
    async def _get_store_metrics(self, store_id: UUID, days: int) -> Dict[str, Any]:
        """Метрики для конкретного магазина"""
        async with self.db.pool.acquire() as conn:
            # Статистика сообщений
            message_stats = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_messages,
                    COUNT(CASE WHEN status = 'sent' THEN 1 END) as sent_messages,
                    COUNT(CASE WHEN status = 'delivered' THEN 1 END) as delivered_messages,
                    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_messages,
                    AVG(CASE WHEN delivered_at IS NOT NULL 
                        THEN EXTRACT(EPOCH FROM (delivered_at - sent_at)) 
                        END) as avg_delivery_time_seconds
                FROM whatsapp_messages_log
                WHERE store_id = $1 AND sent_at >= NOW() - INTERVAL '%s days'
            """, store_id, days)
            
            # Статистика по дням
            daily_stats = await conn.fetch("""
                SELECT 
                    DATE(sent_at) as date,
                    COUNT(*) as messages_count,
                    COUNT(CASE WHEN status = 'sent' THEN 1 END) as sent_count,
                    COUNT(CASE WHEN status = 'delivered' THEN 1 END) as delivered_count,
                    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_count
                FROM whatsapp_messages_log
                WHERE store_id = $1 AND sent_at >= NOW() - INTERVAL '%s days'
                GROUP BY DATE(sent_at)
                ORDER BY date DESC
            """, store_id, days)
            
            # Информация о сессии
            session_info = await self.db.get_session_info(store_id)
            
            return {
                "store_id": str(store_id),
                "period_days": days,
                "message_statistics": dict(message_stats) if message_stats else {},
                "daily_statistics": [dict(row) for row in daily_stats],
                "session_info": session_info.dict() if session_info else None,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _get_global_metrics(self, days: int) -> Dict[str, Any]:
        """Общие метрики системы"""
        async with self.db.pool.acquire() as conn:
            # Общая статистика сообщений
            global_stats = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_messages,
                    COUNT(CASE WHEN status = 'sent' THEN 1 END) as sent_messages,
                    COUNT(CASE WHEN status = 'delivered' THEN 1 END) as delivered_messages,
                    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_messages,
                    COUNT(DISTINCT store_id) as active_stores
                FROM whatsapp_messages_log
                WHERE sent_at >= NOW() - INTERVAL '%s days'
            """, days)
            
            # Статистика по магазинам
            store_stats = await conn.fetch("""
                SELECT 
                    store_id,
                    COUNT(*) as messages_count,
                    COUNT(CASE WHEN status = 'sent' THEN 1 END) as sent_count,
                    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_count
                FROM whatsapp_messages_log
                WHERE sent_at >= NOW() - INTERVAL '%s days'
                GROUP BY store_id
                ORDER BY messages_count DESC
            """, days)
            
            # Статистика шаблонов
            template_stats = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_templates,
                    COUNT(CASE WHEN is_active = TRUE THEN 1 END) as active_templates
                FROM whatsapp_templates
            """)
            
            return {
                "period_days": days,
                "global_statistics": dict(global_stats) if global_stats else {},
                "store_statistics": [dict(row) for row in store_stats],
                "template_statistics": dict(template_stats) if template_stats else {},
                "timestamp": datetime.now().isoformat()
            }
    
    async def generate_report(self, store_id: Optional[UUID] = None, days: int = 30) -> Dict[str, Any]:
        """Генерация отчета"""
        try:
            metrics = await self.get_detailed_metrics(store_id, days)
            health_status = await self.get_health_status()
            
            # Вычисляем дополнительные показатели
            if store_id and "message_statistics" in metrics:
                stats = metrics["message_statistics"]
                total = stats.get("total_messages", 0)
                sent = stats.get("sent_messages", 0)
                delivered = stats.get("delivered_messages", 0)
                failed = stats.get("failed_messages", 0)
                
                success_rate = (sent / total * 100) if total > 0 else 0
                delivery_rate = (delivered / sent * 100) if sent > 0 else 0
                failure_rate = (failed / total * 100) if total > 0 else 0
                
                metrics["calculated_metrics"] = {
                    "success_rate_percent": round(success_rate, 2),
                    "delivery_rate_percent": round(delivery_rate, 2),
                    "failure_rate_percent": round(failure_rate, 2)
                }
            
            return {
                "report_type": "store" if store_id else "global",
                "store_id": str(store_id) if store_id else None,
                "period_days": days,
                "generated_at": datetime.now().isoformat(),
                "health_status": health_status,
                "metrics": metrics,
                "summary": self._generate_summary(metrics, health_status)
            }
            
        except Exception as e:
            logger.error(f"Ошибка генерации отчета: {e}")
            return {"error": str(e)}
    
    def _generate_summary(self, metrics: Dict[str, Any], health_status: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация краткого резюме"""
        summary = {
            "status": health_status.get("status", "unknown"),
            "active_sessions": health_status.get("active_sessions", 0),
            "total_stores": health_status.get("total_stores", 0),
            "waha_server_available": health_status.get("waha_server", False)
        }
        
        if "message_statistics" in metrics:
            stats = metrics["message_statistics"]
            summary.update({
                "total_messages": stats.get("total_messages", 0),
                "sent_messages": stats.get("sent_messages", 0),
                "failed_messages": stats.get("failed_messages", 0)
            })
        
        return summary


class AlertManager:
    """Менеджер алертов"""
    
    def __init__(self):
        self.config = get_config()
        self.alerts: List[Dict[str, Any]] = []
        self.alert_thresholds = {
            "high_failure_rate": 20,  # Процент неудачных отправок
            "low_delivery_rate": 80,  # Процент доставки
            "session_disconnected": 1,  # Количество отключенных сессий
            "waha_server_down": 1  # WAHA сервер недоступен
        }
    
    async def check_alerts(self, monitor: WAHAMonitor) -> List[Dict[str, Any]]:
        """Проверка алертов"""
        alerts = []
        
        try:
            # Проверяем статус здоровья
            health_status = await monitor.get_health_status()
            
            # Алерт: WAHA сервер недоступен
            if not health_status.get("waha_server", False):
                alerts.append({
                    "type": "waha_server_down",
                    "severity": "critical",
                    "message": "WAHA сервер недоступен",
                    "timestamp": datetime.now().isoformat()
                })
            
            # Алерт: Нет активных сессий
            active_sessions = health_status.get("active_sessions", 0)
            if active_sessions == 0:
                alerts.append({
                    "type": "no_active_sessions",
                    "severity": "warning",
                    "message": "Нет активных WhatsApp сессий",
                    "timestamp": datetime.now().isoformat()
                })
            
            # Проверяем метрики ошибок
            error_stats = health_status.get("error_stats", {})
            error_counts = error_stats.get("error_counts", {})
            
            for error_type, count in error_counts.items():
                threshold = self.alert_thresholds.get(error_type, 10)
                if count >= threshold:
                    alerts.append({
                        "type": f"high_{error_type}",
                        "severity": "warning",
                        "message": f"Высокий уровень ошибок {error_type}: {count}",
                        "timestamp": datetime.now().isoformat(),
                        "count": count,
                        "threshold": threshold
                    })
            
            # Сохраняем алерты
            self.alerts.extend(alerts)
            
            # Ограничиваем количество алертов
            if len(self.alerts) > 100:
                self.alerts = self.alerts[-100:]
            
            return alerts
            
        except Exception as e:
            logger.error(f"Ошибка проверки алертов: {e}")
            return []
    
    def get_recent_alerts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Получение недавних алертов"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_alerts = []
        for alert in self.alerts:
            alert_time = datetime.fromisoformat(alert["timestamp"])
            if alert_time >= cutoff_time:
                recent_alerts.append(alert)
        
        return recent_alerts
    
    def clear_alerts(self):
        """Очистка алертов"""
        self.alerts.clear()


# Глобальные экземпляры
monitor: Optional[WAHAMonitor] = None
alert_manager = AlertManager()


def get_monitor() -> Optional[WAHAMonitor]:
    """Получение экземпляра монитора"""
    return monitor


def get_alert_manager() -> AlertManager:
    """Получение экземпляра менеджера алертов"""
    return alert_manager


async def initialize_monitoring(db: WAHA_Database) -> WAHAMonitor:
    """Инициализация мониторинга"""
    global monitor
    
    if monitor is None:
        monitor = WAHAMonitor(db)
        await monitor.start_monitoring()
    
    return monitor


async def shutdown_monitoring():
    """Завершение мониторинга"""
    global monitor
    
    if monitor:
        await monitor.stop_monitoring()
        monitor = None
