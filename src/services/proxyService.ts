// services/proxyService.ts
// Сервис для управления прокси системой

import { API_URL, API_BASE_PATH } from '@/config';
import { API_ENDPOINTS, buildApiUrl } from '@/config/api';

export interface ProxyInfo {
  id: string;
  host: string;
  port: number;
  username?: string;
  status: 'active' | 'blocked' | 'error' | 'maintenance';
  success_count: number;
  error_count: number;
  success_rate: number;
  last_used?: string;
  last_error?: string;
}

export interface ProxyStatistics {
  total_proxies: number;
  active_proxies: number;
  blocked_proxies: number;
  total_success: number;
  total_errors: number;
  overall_success_rate: number;
  last_reset: string;
  proxies: ProxyInfo[];
}

export interface ProxyHealth {
  status: 'healthy' | 'degraded' | 'warning' | 'critical' | 'disabled';
  message: string;
  active_count: number;
  avg_success_rate?: number;
  total_proxies: number;
}

export interface ProxyStatus {
  enabled: boolean;
  total_proxies: number;
  active_proxies: number;
  timestamp: string;
}

export interface AddProxyRequest {
  proxy_id: string;
  host: string;
  port: number;
  username?: string;
  password?: string;
}

class ProxyService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = `${API_URL}${API_BASE_PATH}`;
  }

  /**
   * Получить статус прокси системы
   */
  async getProxyStatus(): Promise<ProxyStatus> {
    try {
      const response = await fetch(buildApiUrl(API_ENDPOINTS.proxy.status));

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Ошибка получения статуса прокси');
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting proxy status:', error);
      throw error;
    }
  }

  /**
   * Получить статистику прокси
   */
  async getProxyStatistics(): Promise<ProxyStatistics> {
    try {
      const response = await fetch(buildApiUrl(API_ENDPOINTS.proxy.statistics));

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Ошибка получения статистики прокси');
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting proxy statistics:', error);
      throw error;
    }
  }

  /**
   * Проверка здоровья прокси системы
   */
  async getProxyHealth(): Promise<ProxyHealth> {
    try {
      const response = await fetch(buildApiUrl(API_ENDPOINTS.proxy.health));

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Ошибка проверки здоровья прокси');
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting proxy health:', error);
      throw error;
    }
  }

  /**
   * Добавить новый прокси
   */
  async addProxy(request: AddProxyRequest): Promise<{ success: boolean; message: string; proxy_id: string }> {
    try {
      const response = await fetch(buildApiUrl(API_ENDPOINTS.proxy.add), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Ошибка добавления прокси');
      }

      return await response.json();
    } catch (error) {
      console.error('Error adding proxy:', error);
      throw error;
    }
  }

  /**
   * Удалить прокси
   */
  async removeProxy(proxyId: string): Promise<{ success: boolean; message: string; proxy_id: string }> {
    try {
      const response = await fetch(buildApiUrl(API_ENDPOINTS.proxy.remove), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ proxy_id: proxyId }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Ошибка удаления прокси');
      }

      return await response.json();
    } catch (error) {
      console.error('Error removing proxy:', error);
      throw error;
    }
  }

  /**
   * Разблокировать прокси
   */
  async unblockProxy(proxyId: string): Promise<{ success: boolean; message: string; proxy_id: string }> {
    try {
      const response = await fetch(buildApiUrl(API_ENDPOINTS.proxy.unblock), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ proxy_id: proxyId }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Ошибка разблокировки прокси');
      }

      return await response.json();
    } catch (error) {
      console.error('Error unblocking proxy:', error);
      throw error;
    }
  }

  /**
   * Получить список всех прокси
   */
  async listProxies(): Promise<ProxyInfo[]> {
    try {
      const response = await fetch(buildApiUrl(API_ENDPOINTS.proxy.list));

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Ошибка получения списка прокси');
      }

      return await response.json();
    } catch (error) {
      console.error('Error listing proxies:', error);
      throw error;
    }
  }

  /**
   * Протестировать прокси
   */
  async testProxy(proxyId: string): Promise<{ 
    success: boolean; 
    message: string; 
    proxy_id: string; 
    proxy_url: string; 
    timestamp: string; 
  }> {
    try {
      const response = await fetch(buildApiUrl(API_ENDPOINTS.proxy.test(proxyId)));

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Ошибка тестирования прокси');
      }

      return await response.json();
    } catch (error) {
      console.error('Error testing proxy:', error);
      throw error;
    }
  }

  /**
   * Сбросить статистику прокси
   */
  async resetProxyStatistics(): Promise<{ success: boolean; message: string; timestamp: string }> {
    try {
      const response = await fetch(buildApiUrl(API_ENDPOINTS.proxy.resetStats), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Ошибка сброса статистики прокси');
      }

      return await response.json();
    } catch (error) {
      console.error('Error resetting proxy statistics:', error);
      throw error;
    }
  }

  /**
   * Создать запрос на добавление прокси с валидацией
   */
  createAddProxyRequest(proxyId: string, host: string, port: number, username?: string, password?: string): AddProxyRequest {
    return {
      proxy_id: proxyId,
      host,
      port,
      username,
      password,
    };
  }

  /**
   * Валидация данных прокси
   */
  validateProxyData(data: AddProxyRequest): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (!data.proxy_id || data.proxy_id.trim() === '') {
      errors.push('ID прокси обязателен');
    }

    if (!data.host || data.host.trim() === '') {
      errors.push('Хост прокси обязателен');
    }

    if (!data.port || data.port < 1 || data.port > 65535) {
      errors.push('Порт прокси должен быть от 1 до 65535');
    }

    // Проверка формата хоста (базовая валидация)
    if (data.host && !/^[a-zA-Z0-9.-]+$/.test(data.host)) {
      errors.push('Неверный формат хоста');
    }

    return {
      valid: errors.length === 0,
      errors,
    };
  }

  /**
   * Получить активные прокси из списка
   */
  getActiveProxies(proxies: ProxyInfo[]): ProxyInfo[] {
    return proxies.filter(proxy => proxy.status === 'active');
  }

  /**
   * Получить заблокированные прокси из списка
   */
  getBlockedProxies(proxies: ProxyInfo[]): ProxyInfo[] {
    return proxies.filter(proxy => proxy.status === 'blocked');
  }

  /**
   * Сортировать прокси по успешности
   */
  sortProxiesBySuccess(proxies: ProxyInfo[]): ProxyInfo[] {
    return [...proxies].sort((a, b) => b.success_rate - a.success_rate);
  }

  /**
   * Получить топ N прокси по успешности
   */
  getTopProxies(proxies: ProxyInfo[], limit: number = 5): ProxyInfo[] {
    return this.sortProxiesBySuccess(proxies).slice(0, limit);
  }
}

export const proxyService = new ProxyService();
export default proxyService;
