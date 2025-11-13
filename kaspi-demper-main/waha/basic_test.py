#!/usr/bin/env python3
"""
Упрощенный тест WAHA модуля - только основные компоненты
"""

import sys
import os
import uuid
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_basic_imports():
    """Тест базовых импортов"""
    print("🔍 Тестирование базовых импортов...")
    
    try:
        import models
        print("✅ Модели импортированы успешно")
    except Exception as e:
        print(f"❌ Ошибка импорта моделей: {e}")
        return False
    
    try:
        import config
        print("✅ Конфигурация импортирована успешно")
    except Exception as e:
        print(f"❌ Ошибка импорта конфигурации: {e}")
        return False
    
    return True

def test_models_creation():
    """Тест создания моделей"""
    print("\n🔍 Тестирование создания моделей...")
    
    try:
        import models
        
        # Тест создания шаблона
        template = models.WhatsAppTemplate(
            template_name="test_template",
            template_text="Здравствуйте, {user_name}! Ваш заказ {order_num} готов.",
            store_id=str(uuid.uuid4())
        )
        print("✅ Шаблон создан успешно")
        
        # Тест создания данных заказа
        order = models.OrderData(
            order_id="12345",
            user_name="Иван Иванов",
            order_num="ORD-001",
            product_name="Тестовый товар",
            item_qty=2,
            shop_name="Мой магазин"
        )
        print("✅ Данные заказа созданы успешно")
        
        # Тест создания настроек
        settings = models.WAHASettings(
            waha_server_url="http://localhost:3000",
            webhook_url="http://localhost:8000/webhook"
        )
        print("✅ Настройки созданы успешно")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка создания моделей: {e}")
        return False

def test_config():
    """Тест конфигурации"""
    print("\n🔍 Тестирование конфигурации...")
    
    try:
        import config
        
        settings = config.WAHASettings()
        print(f"✅ WAHA URL: {settings.waha_server_url}")
        print(f"✅ Webhook URL: {settings.webhook_base_url}")
        print(f"✅ Max messages: {settings.max_messages_per_day}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка конфигурации: {e}")
        return False

def test_template_validation():
    """Тест валидации шаблонов"""
    print("\n🔍 Тестирование валидации шаблонов...")
    
    try:
        import models
        
        # Тест валидного шаблона
        valid_template = models.WhatsAppTemplate(
            template_name="valid_template",
            template_text="Здравствуйте, {user_name}! Ваш заказ {order_num} готов к самовывозу.",
            store_id=str(uuid.uuid4())
        )
        print("✅ Валидный шаблон прошел проверку")
        
        # Тест невалидного шаблона (пустой текст)
        try:
            invalid_template = models.WhatsAppTemplate(
                template_name="invalid_template",
                template_text="",  # Пустой текст
                store_id=str(uuid.uuid4())
            )
            print("❌ Невалидный шаблон не должен был пройти проверку")
            return False
        except Exception:
            print("✅ Невалидный шаблон правильно отклонен")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка валидации шаблонов: {e}")
        return False

def test_order_data():
    """Тест данных заказа"""
    print("\n🔍 Тестирование данных заказа...")
    
    try:
        import models
        
        # Тест создания данных заказа
        order = models.OrderData(
            order_id="ORD-12345",
            user_name="Айдар Нурланов",
            order_num="ORD-001",
            product_name="iPhone 15 Pro",
            item_qty=1,
            shop_name="TechStore Kazakhstan"
        )
        
        print(f"✅ Заказ создан: {order.order_id}")
        print(f"✅ Покупатель: {order.user_name}")
        print(f"✅ Товар: {order.product_name}")
        print(f"✅ Количество: {order.item_qty}")
        print(f"✅ Магазин: {order.shop_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка создания данных заказа: {e}")
        return False

def test_message_template():
    """Тест шаблона сообщения"""
    print("\n🔍 Тестирование шаблона сообщения...")
    
    try:
        import models
        
        # Создаем шаблон с переменными
        template = models.WhatsAppTemplate(
            template_name="order_ready_template",
            template_text="""Здравствуйте, {user_name}.
Ваш заказ Nº {order_num} "{product_name}", количество: {item_qty} шт готов к самовывозу.

* В ближайшее время мы свяжемся с вами для уточнения деталей заказа.
* Спасибо за Ваш выбор! Если у Вас есть вопросы, обращайтесь в любое время.

С уважением,
{shop_name}""",
            store_id=str(uuid.uuid4())
        )
        
        print("✅ Шаблон сообщения создан успешно")
        print(f"✅ Название: {template.template_name}")
        print(f"✅ Длина текста: {len(template.template_text)} символов")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка создания шаблона сообщения: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🚀 Запуск упрощенного теста WAHA модуля\n")
    
    tests = [
        test_basic_imports,
        test_models_creation,
        test_config,
        test_template_validation,
        test_order_data,
        test_message_template
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Результаты: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 Все тесты пройдены успешно!")
        print("✅ WAHA модуль готов к использованию!")
        return True
    else:
        print("⚠️  Некоторые тесты не пройдены")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
