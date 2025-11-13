# template_manager.py
"""
Менеджер шаблонов WhatsApp сообщений
"""

import re
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import UUID

from .models import WhatsAppTemplate, WhatsAppTemplateCreate, WhatsAppTemplateUpdate, WhatsAppTemplatePreview
from .database import WAHA_Database

logger = logging.getLogger(__name__)


class TemplateManager:
    """Менеджер шаблонов WhatsApp сообщений"""
    
    def __init__(self, db: WAHA_Database):
        self.db = db
        self.available_variables = {
            '{user_name}': 'Имя покупателя',
            '{order_num}': 'Номер заказа',
            '{product_name}': 'Название товара',
            '{item_qty}': 'Количество товара',
            '{shop_name}': 'Название магазина',
            '{delivery_type}': 'Тип доставки',
            '{order_date}': 'Дата заказа',
            '{total_amount}': 'Общая сумма заказа',
            '{customer_phone}': 'Телефон покупателя'
        }
    
    async def create_template(self, store_id: UUID, template_data: WhatsAppTemplateCreate) -> WhatsAppTemplate:
        """Создание нового шаблона"""
        try:
            # Валидация шаблона
            self._validate_template(template_data.template_text)
            
            template = WhatsAppTemplate(
                store_id=store_id,
                template_name=template_data.template_name,
                template_text=template_data.template_text,
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            template_id = await self.db.create_template(template)
            template.id = template_id
            
            logger.info(f"Создан шаблон '{template_data.template_name}' для магазина {store_id}")
            return template
            
        except Exception as e:
            logger.error(f"Ошибка создания шаблона для магазина {store_id}: {e}")
            raise
    
    async def get_templates(self, store_id: UUID) -> List[WhatsAppTemplate]:
        """Получение всех шаблонов магазина"""
        try:
            templates = await self.db.get_templates(store_id)
            return templates
        except Exception as e:
            logger.error(f"Ошибка получения шаблонов для магазина {store_id}: {e}")
            raise
    
    async def get_template(self, template_id: UUID) -> Optional[WhatsAppTemplate]:
        """Получение шаблона по ID"""
        try:
            template = await self.db.get_template(template_id)
            return template
        except Exception as e:
            logger.error(f"Ошибка получения шаблона {template_id}: {e}")
            raise
    
    async def update_template(self, template_id: UUID, template_data: WhatsAppTemplateUpdate) -> WhatsAppTemplate:
        """Обновление шаблона"""
        try:
            # Получаем существующий шаблон
            existing_template = await self.db.get_template(template_id)
            if not existing_template:
                raise ValueError("Шаблон не найден")
            
            # Обновляем поля
            update_data = {}
            if template_data.template_name is not None:
                update_data['template_name'] = template_data.template_name
            if template_data.template_text is not None:
                self._validate_template(template_data.template_text)
                update_data['template_text'] = template_data.template_text
            if template_data.is_active is not None:
                update_data['is_active'] = template_data.is_active
            
            update_data['updated_at'] = datetime.now()
            
            await self.db.update_template(template_id, update_data)
            
            # Возвращаем обновленный шаблон
            updated_template = await self.db.get_template(template_id)
            logger.info(f"Обновлен шаблон {template_id}")
            return updated_template
            
        except Exception as e:
            logger.error(f"Ошибка обновления шаблона {template_id}: {e}")
            raise
    
    async def delete_template(self, template_id: UUID) -> bool:
        """Удаление шаблона"""
        try:
            result = await self.db.delete_template(template_id)
            logger.info(f"Удален шаблон {template_id}")
            return result
        except Exception as e:
            logger.error(f"Ошибка удаления шаблона {template_id}: {e}")
            raise
    
    async def get_active_template(self, store_id: UUID) -> Optional[WhatsAppTemplate]:
        """Получение активного шаблона магазина"""
        try:
            template = await self.db.get_active_template(store_id)
            return template
        except Exception as e:
            logger.error(f"Ошибка получения активного шаблона для магазина {store_id}: {e}")
            raise
    
    def process_template(self, template_text: str, order_data: Dict[str, Any]) -> str:
        """
        Обработка шаблона с подстановкой переменных
        
        Args:
            template_text: Текст шаблона
            order_data: Данные заказа для подстановки
            
        Returns:
            Обработанный текст сообщения
        """
        try:
            # Подготавливаем данные для подстановки
            replacements = {
                '{user_name}': order_data.get('customer_name', 'Клиент'),
                '{order_num}': order_data.get('order_id', 'N/A'),
                '{product_name}': order_data.get('product_name', 'Товар'),
                '{item_qty}': str(order_data.get('quantity', 1)),
                '{shop_name}': order_data.get('shop_name', 'Магазин'),
                '{delivery_type}': order_data.get('delivery_type', 'самовывоз'),
                '{order_date}': order_data.get('order_date', datetime.now().strftime('%d.%m.%Y')),
                '{total_amount}': str(order_data.get('total_amount', 0)),
                '{customer_phone}': order_data.get('customer_phone', '')
            }
            
            # Выполняем подстановку
            message = template_text
            for placeholder, value in replacements.items():
                message = message.replace(placeholder, str(value))
            
            # Проверяем, что все переменные заменены
            remaining_vars = re.findall(r'\{[^}]+\}', message)
            if remaining_vars:
                logger.warning(f"Незамененные переменные в шаблоне: {remaining_vars}")
            
            return message
            
        except Exception as e:
            logger.error(f"Ошибка обработки шаблона: {e}")
            raise
    
    def preview_template(self, template_text: str, sample_data: Dict[str, Any]) -> WhatsAppTemplatePreview:
        """
        Предварительный просмотр шаблона
        
        Args:
            template_text: Текст шаблона
            sample_data: Тестовые данные
            
        Returns:
            Предварительный просмотр с подстановкой
        """
        try:
            preview_text = self.process_template(template_text, sample_data)
            
            return WhatsAppTemplatePreview(
                template_text=template_text,
                sample_data=sample_data,
                preview_text=preview_text
            )
            
        except Exception as e:
            logger.error(f"Ошибка предварительного просмотра шаблона: {e}")
            raise
    
    def get_available_variables(self) -> Dict[str, str]:
        """Получение списка доступных переменных"""
        return self.available_variables.copy()
    
    def validate_template_variables(self, template_text: str) -> Dict[str, Any]:
        """
        Валидация переменных в шаблоне
        
        Args:
            template_text: Текст шаблона
            
        Returns:
            Результат валидации
        """
        try:
            # Находим все переменные в шаблоне
            found_variables = re.findall(r'\{[^}]+\}', template_text)
            
            # Проверяем, какие переменные известны
            known_variables = []
            unknown_variables = []
            
            for var in found_variables:
                if var in self.available_variables:
                    known_variables.append(var)
                else:
                    unknown_variables.append(var)
            
            return {
                'valid': len(unknown_variables) == 0,
                'known_variables': known_variables,
                'unknown_variables': unknown_variables,
                'total_variables': len(found_variables)
            }
            
        except Exception as e:
            logger.error(f"Ошибка валидации переменных шаблона: {e}")
            raise
    
    def _validate_template(self, template_text: str) -> None:
        """Валидация шаблона"""
        if not template_text or not template_text.strip():
            raise ValueError("Текст шаблона не может быть пустым")
        
        # Проверяем переменные
        validation_result = self.validate_template_variables(template_text)
        if not validation_result['valid']:
            unknown_vars = ', '.join(validation_result['unknown_variables'])
            raise ValueError(f"Неизвестные переменные в шаблоне: {unknown_vars}")
    
    def get_default_template(self) -> str:
        """Получение шаблона по умолчанию"""
        return """Здравствуйте, {user_name}!
Ваш заказ Nº {order_num} "{product_name}", количество: {item_qty} шт готов к самовывозу.
* В ближайшее время мы свяжемся с вами для уточнения деталей заказа.
* Спасибо за Ваш выбор! Если у Вас есть вопросы, обращайтесь в любое время.
С уважением,
{shop_name}"""
    
    def get_sample_order_data(self) -> Dict[str, Any]:
        """Получение тестовых данных заказа"""
        return {
            'customer_name': 'Иван Иванов',
            'customer_phone': '+7XXXXXXXXXX',
            'order_id': '12345',
            'product_name': 'Тестовый товар',
            'quantity': 2,
            'total_amount': 5000.0,
            'delivery_type': 'самовывоз',
            'order_date': datetime.now().strftime('%d.%m.%Y'),
            'shop_name': 'Мой магазин Kaspi'
        }
