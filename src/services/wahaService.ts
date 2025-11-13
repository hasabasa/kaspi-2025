// services/wahaService.ts
/**
 * Сервис для работы с WAHA WhatsApp API
 */

import { API_BASE_URL } from '../config';

export interface WAHASession {
  session_id: string;
  status: string;
  phone?: string;
  is_connected: boolean;
  created_at: string;
  expires_at?: string;
}

export interface WhatsAppTemplate {
  id: number;
  store_id: string;
  template_name: string;
  template_text: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface TemplateCreate {
  template_name: string;
  template_text: string;
}

export interface TemplateUpdate {
  template_name?: string;
  template_text?: string;
  is_active?: boolean;
}

export interface TestMessage {
  phone_number: string;
  template_text: string;
  sample_data: Record<string, any>;
}

export interface TemplatePreview {
  template_text: string;
  sample_data: Record<string, any>;
  preview_text: string;
}

export interface AvailableVariables {
  [key: string]: string;
}

class WAHAService {
  private baseUrl = `${API_BASE_URL}/api/v1/waha`;

  /**
   * Начать подключение WhatsApp сессии
   */
  async startSession(storeId: string, phoneNumber: string): Promise<{
    success: boolean;
    session_id: string;
    pairing_code: string;
    expires_at: string;
    instructions: string;
  }> {
    const response = await fetch(`${this.baseUrl}/sessions/start`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        store_id: storeId,
        phone_number: phoneNumber,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Ошибка создания сессии');
    }

    return response.json();
  }

  /**
   * Получить статус сессии
   */
  async getSessionStatus(sessionId: string): Promise<WAHASession> {
    const response = await fetch(`${this.baseUrl}/sessions/status/${sessionId}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Ошибка получения статуса сессии');
    }

    return response.json();
  }

  /**
   * Удалить сессию
   */
  async deleteSession(sessionId: string): Promise<{ success: boolean; message: string }> {
    const response = await fetch(`${this.baseUrl}/sessions/${sessionId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Ошибка удаления сессии');
    }

    return response.json();
  }

  /**
   * Создать шаблон сообщения
   */
  async createTemplate(storeId: string, template: TemplateCreate): Promise<{
    success: boolean;
    template_id: number;
    message: string;
  }> {
    const response = await fetch(`${this.baseUrl}/templates`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        store_id: storeId,
        ...template,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Ошибка создания шаблона');
    }

    return response.json();
  }

  /**
   * Получить список шаблонов
   */
  async getTemplates(storeId: string): Promise<WhatsAppTemplate[]> {
    const response = await fetch(`${this.baseUrl}/templates?store_id=${storeId}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Ошибка получения шаблонов');
    }

    return response.json();
  }

  /**
   * Обновить шаблон
   */
  async updateTemplate(templateId: number, template: TemplateUpdate): Promise<{
    success: boolean;
    message: string;
  }> {
    const response = await fetch(`${this.baseUrl}/templates/${templateId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(template),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Ошибка обновления шаблона');
    }

    return response.json();
  }

  /**
   * Удалить шаблон
   */
  async deleteTemplate(templateId: number): Promise<{ success: boolean; message: string }> {
    const response = await fetch(`${this.baseUrl}/templates/${templateId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Ошибка удаления шаблона');
    }

    return response.json();
  }

  /**
   * Отправить тестовое сообщение
   */
  async sendTestMessage(storeId: string, testMessage: TestMessage): Promise<{
    success: boolean;
    message_id?: string;
    error?: string;
  }> {
    const response = await fetch(`${this.baseUrl}/send-test`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        store_id: storeId,
        ...testMessage,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Ошибка отправки тестового сообщения');
    }

    return response.json();
  }

  /**
   * Предварительный просмотр шаблона
   */
  async previewTemplate(
    templateText: string,
    sampleData?: Record<string, any>
  ): Promise<TemplatePreview> {
    const response = await fetch(`${this.baseUrl}/templates/preview`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        template_text: templateText,
        sample_data: sampleData,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Ошибка предварительного просмотра');
    }

    return response.json();
  }

  /**
   * Получить доступные переменные
   */
  async getAvailableVariables(): Promise<AvailableVariables> {
    const response = await fetch(`${this.baseUrl}/variables`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Ошибка получения переменных');
    }

    return response.json();
  }
}

export const wahaService = new WAHAService();