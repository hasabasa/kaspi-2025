// services/whatsappService.ts
interface WhatsAppSession {
  name: string;
  store_id: string;
  status: string;
  created_at: string;
  updated_at?: string;
}

interface WhatsAppMessage {
  session: string;
  chatId: string;
  text: string;
}

interface BulkMessage {
  session: string;
  phone_numbers: string[];
  message_template: string;
  variables: Record<string, any>;
}

interface MessageTemplate {
  id: string;
  name: string;
  content: string;
  variables: string[];
  category: string;
}

interface WhatsAppCampaign {
  id?: number;
  name: string;
  store_id: string;
  session_name: string;
  template_id: string;
  template_variables: Record<string, any>;
  recipient_list: string[];
  status?: string;
  scheduled_at?: string;
}

interface MessageHistory {
  id: number;
  session_name: string;
  chat_id: string;
  message_text: string;
  status: string;
  sent_at: string;
  error_message?: string;
}

interface WhatsAppResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

class WhatsAppService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8010';
  }

  /**
   * Создать новую WhatsApp сессию
   */
  async createSession(name: string, storeId: string): Promise<WhatsAppResponse<any>> {
    try {
      const response = await fetch(`${this.baseUrl}/whatsapp/sessions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name,
          store_id: storeId
        })
      });

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error creating WhatsApp session:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  /**
   * Получить статус сессии и QR код
   */
  async getSessionStatus(sessionName: string): Promise<WhatsAppResponse<any>> {
    try {
      const response = await fetch(`${this.baseUrl}/whatsapp/sessions/${sessionName}/status`);
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error getting session status:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  /**
   * Получить все сессии
   */
  async getSessions(): Promise<WhatsAppResponse<WhatsAppSession[]>> {
    try {
      const response = await fetch(`${this.baseUrl}/whatsapp/sessions`);
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error getting sessions:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  /**
   * Отправить одиночное сообщение
   */
  async sendMessage(message: WhatsAppMessage): Promise<WhatsAppResponse<any>> {
    try {
      const response = await fetch(`${this.baseUrl}/whatsapp/send-message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(message)
      });

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error sending message:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  /**
   * Отправить массовые сообщения
   */
  async sendBulkMessages(bulkMessage: BulkMessage): Promise<WhatsAppResponse<any>> {
    try {
      const response = await fetch(`${this.baseUrl}/whatsapp/send-bulk`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(bulkMessage)
      });

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error sending bulk messages:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  /**
   * Получить шаблоны сообщений
   */
  async getTemplates(): Promise<WhatsAppResponse<MessageTemplate[]>> {
    try {
      const response = await fetch(`${this.baseUrl}/whatsapp/templates`);
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error getting templates:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  /**
   * Создать шаблон сообщения
   */
  async createTemplate(template: MessageTemplate): Promise<WhatsAppResponse<any>> {
    try {
      const response = await fetch(`${this.baseUrl}/whatsapp/templates`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(template)
      });

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error creating template:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  /**
   * Получить историю сообщений
   */
  async getMessageHistory(
    sessionName?: string,
    limit: number = 100,
    offset: number = 0
  ): Promise<WhatsAppResponse<MessageHistory[]>> {
    try {
      const params = new URLSearchParams({
        limit: limit.toString(),
        offset: offset.toString()
      });
      
      if (sessionName) {
        params.append('session_name', sessionName);
      }

      const response = await fetch(`${this.baseUrl}/whatsapp/messages/history?${params}`);
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error getting message history:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  /**
   * Извлечь номера телефонов из данных продаж (демо функция)
   */
  extractPhoneNumbers(salesData: any[]): string[] {
    // Это демо-функция. В реальности номера телефонов должны 
    // извлекаться из данных о клиентах Kaspi
    const demoPhones = [
      '77771234567',
      '77019876543',
      '77475551234',
      '77123456789',
      '77987654321'
    ];
    
    return demoPhones;
  }

  /**
   * Подготовить переменные для шаблона из данных продаж
   */
  prepareTemplateVariables(templateId: string, salesData: any, storeData?: any): Record<string, any> {
    const now = new Date();
    const baseVariables = {
      timestamp: now.toLocaleString('ru'),
      date: now.toLocaleDateString('ru'),
      store_name: storeData?.name || 'Ваш магазин'
    };

    switch (templateId) {
      case 'daily_sales_summary':
        return {
          ...baseVariables,
          revenue: this.formatPrice(salesData.totalRevenue || 0),
          orders_count: salesData.totalOrders || 0,
          avg_check: this.formatPrice(salesData.avgOrderValue || 0),
          top_products: this.formatTopProducts(salesData.topProducts || [])
        };

      case 'new_order_alert':
        return {
          ...baseVariables,
          order_amount: this.formatPrice(salesData.amount || 0),
          product_name: salesData.productName || 'Товар'
        };

      case 'price_bot_alert':
        return {
          ...baseVariables,
          product_name: salesData.productName || 'Товар',
          old_price: this.formatPrice(salesData.oldPrice || 0),
          new_price: this.formatPrice(salesData.newPrice || 0),
          competitor_price: this.formatPrice(salesData.competitorPrice || 0)
        };

      case 'weekly_report':
        return {
          ...baseVariables,
          week_dates: salesData.weekDates || 'Эта неделя',
          total_revenue: this.formatPrice(salesData.totalRevenue || 0),
          total_orders: salesData.totalOrders || 0,
          growth_percent: salesData.growthPercent || 0,
          top_products: this.formatTopProducts(salesData.topProducts || []),
          daily_stats: this.formatDailyStats(salesData.dailyStats || [])
        };

      default:
        return baseVariables;
    }
  }

  /**
   * Форматировать цену
   */
  private formatPrice(price: number): string {
    return new Intl.NumberFormat('ru-KZ').format(price) + ' ₸';
  }

  /**
   * Форматировать топ товары для сообщения
   */
  private formatTopProducts(products: any[]): string {
    if (!products.length) return 'Нет данных';
    
    return products
      .slice(0, 5)
      .map((product, index) => 
        `${index + 1}. ${product.name || product.product_name || 'Товар'} - ${product.quantity || 0} шт.`
      )
      .join('\n');
  }

  /**
   * Форматировать ежедневную статистику
   */
  private formatDailyStats(dailyStats: any[]): string {
    if (!dailyStats.length) return 'Нет данных';
    
    return dailyStats
      .slice(0, 7)
      .map(stat => 
        `${stat.date}: ${stat.orders || 0} заказов, ${this.formatPrice(stat.revenue || 0)}`
      )
      .join('\n');
  }

  /**
   * Валидация номера телефона
   */
  validatePhoneNumber(phone: string): boolean {
    // Удаляем все нецифровые символы
    const cleanPhone = phone.replace(/\D/g, '');
    
    // Проверяем длину и формат (казахстанские номера)
    return /^7\d{10}$/.test(cleanPhone);
  }

  /**
   * Форматирование номера телефона
   */
  formatPhoneNumber(phone: string): string {
    const cleanPhone = phone.replace(/\D/g, '');
    
    if (cleanPhone.length === 10) {
      return '7' + cleanPhone;
    }
    
    return cleanPhone;
  }

  /**
   * Предпросмотр сообщения с переменными
   */
  previewMessage(template: string, variables: Record<string, any>): string {
    let preview = template;
    
    Object.entries(variables).forEach(([key, value]) => {
      const placeholder = `{${key}}`;
      preview = preview.replace(new RegExp(placeholder, 'g'), String(value));
    });
    
    return preview;
  }
}

export const whatsappService = new WhatsAppService();
export type { 
  WhatsAppSession, 
  WhatsAppMessage, 
  BulkMessage, 
  MessageTemplate, 
  WhatsAppCampaign, 
  MessageHistory, 
  WhatsAppResponse 
};
