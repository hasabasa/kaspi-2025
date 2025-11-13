// config/waha.ts
export const WAHA_CONFIG = {
  // URL WAHA сервера (по умолчанию localhost:3000)
  API_ENDPOINT: import.meta.env.VITE_WAHA_API_ENDPOINT || 'http://localhost:3000',
  
  // ID сессии WhatsApp
  SESSION_ID: import.meta.env.VITE_WAHA_SESSION_ID || 'kaspi-whatsapp-session',
  
  // Webhook URL для получения событий (будет настроен в WAHA сервере)
  WEBHOOK_URL: import.meta.env.VITE_WEBHOOK_URL || 'http://localhost:3000/webhook',
  
  // Настройки по умолчанию
  DEFAULT_SETTINGS: {
    // Автоматические ответы
    AUTO_REPLY: true,
    
    // Максимальное количество сообщений в день
    MAX_MESSAGES_PER_DAY: 1000,
    
    // Интервал между сообщениями (в миллисекундах)
    MESSAGE_INTERVAL: 1000,
    
    // Время работы (в часах)
    WORKING_HOURS: {
      START: 9,
      END: 21
    },
    
    // Дни недели для работы (1 = понедельник, 7 = воскресенье)
    WORKING_DAYS: [1, 2, 3, 4, 5, 6, 7]
  },
  
  // Шаблоны сообщений по умолчанию
  DEFAULT_TEMPLATES: [
    {
      name: 'Уведомление о заказе',
      content: 'Здравствуйте, {user_name}!\n\nВаш заказ №{order_num} "{product_name}", количество: {item_qty} шт готов к самовывозу.\n\n* В ближайшее время мы свяжемся с вами для уточнения деталей заказа.\n* Спасибо за Ваш выбор! Если у Вас есть вопросы, обращайтесь в любое время.\n\nС уважением,\n{shop_name}',
      variables: ['user_name', 'order_num', 'product_name', 'item_qty', 'shop_name'],
      isActive: true
    },
    {
      name: 'Уведомление о доставке',
      content: 'Здравствуйте, {user_name}!\n\nВаш заказ №{order_num} отправлен и будет доставлен в течение 1-2 рабочих дней.\n\nТрек-номер: {tracking_number}\n\nСпасибо за покупку!\n\nС уважением,\n{shop_name}',
      variables: ['user_name', 'order_num', 'tracking_number', 'shop_name'],
      isActive: true
    },
    {
      name: 'Напоминание о заказе',
      content: 'Здравствуйте, {user_name}!\n\nНапоминаем, что ваш заказ №{order_num} готов к самовывозу.\n\nПожалуйста, заберите заказ в течение 3 дней.\n\nС уважением,\n{shop_name}',
      variables: ['user_name', 'order_num', 'shop_name'],
      isActive: true
    }
  ],
  
  // Настройки безопасности
  SECURITY: {
    // Разрешенные номера телефонов (если пустой массив - все номера разрешены)
    ALLOWED_PHONES: [],
    
    // Запрещенные номера телефонов
    BLOCKED_PHONES: [],
    
    // Максимальная длина сообщения
    MAX_MESSAGE_LENGTH: 1000,
    
    // Защита от спама (максимум сообщений в час)
    MAX_MESSAGES_PER_HOUR: 10
  }
};

export default WAHA_CONFIG;
