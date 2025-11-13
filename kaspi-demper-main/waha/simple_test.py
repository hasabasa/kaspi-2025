#!/usr/bin/env python3
"""
Простой тест WAHA модуля без сложных зависимостей
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Тест импорта модулей"""
    print("🔍 Тестирование импортов...")
    
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
    
    try:
        import utils
        print("✅ Утилиты импортированы успешно")
    except Exception as e:
        print(f"❌ Ошибка импорта утилит: {e}")
        return False
    
    return True

def test_models():
    """Тест создания моделей"""
    print("\n🔍 Тестирование моделей...")
    
    try:
        import models
        
        # Тест создания шаблона с обязательными полями
        import uuid
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
        
        return True
    except Exception as e:
        print(f"❌ Ошибка создания моделей: {e}")
        return False

def test_template_processing():
    """Тест обработки шаблонов"""
    print("\n🔍 Тестирование обработки шаблонов...")
    
    try:
        import utils
        
        processor = utils.MessageTemplateProcessor()
        
        template_text = "Здравствуйте, {user_name}!\nВаш заказ {order_num} готов к самовывозу."
        data = {
            "user_name": "Иван Иванов",
            "order_num": "ORD-001"
        }
        
        result = processor.process_template(template_text, data)
        expected = "Здравствуйте, Иван Иванов!\nВаш заказ ORD-001 готов к самовывозу."
        
        if result == expected:
            print("✅ Обработка шаблона работает корректно")
            return True
        else:
            print(f"❌ Неожиданный результат: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка обработки шаблона: {e}")
        return False

def test_phone_validation():
    """Тест валидации номеров телефонов"""
    print("\n🔍 Тестирование валидации номеров...")
    
    try:
        import utils
        
        validator = utils.PhoneNumberValidator()
        
        # Тест казахстанских номеров
        valid_numbers = [
            "+77001234567",
            "77001234567",
            "87001234567"
        ]
        
        invalid_numbers = [
            "123",
            "abc",
            "+1234567890"
        ]
        
        for number in valid_numbers:
            if validator.validate(number):
                print(f"✅ Номер {number} валиден")
            else:
                print(f"❌ Номер {number} должен быть валидным")
                return False
        
        for number in invalid_numbers:
            if not validator.validate(number):
                print(f"✅ Номер {number} правильно отклонен")
            else:
                print(f"❌ Номер {number} не должен быть валидным")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка валидации номеров: {e}")
        return False

def test_config():
    """Тест конфигурации"""
    print("\n🔍 Тестирование конфигурации...")
    
    try:
        import config
        
        config_obj = config.WAHASettings()
        print(f"✅ WAHA URL: {config_obj.waha_server_url}")
        print(f"✅ Webhook URL: {config_obj.webhook_base_url}")
        print(f"✅ Max messages: {config_obj.max_messages_per_day}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка конфигурации: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🚀 Запуск простого теста WAHA модуля\n")
    
    tests = [
        test_imports,
        test_models,
        test_template_processing,
        test_phone_validation,
        test_config
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
        return True
    else:
        print("⚠️  Некоторые тесты не пройдены")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
