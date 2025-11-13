// services/demperService.ts
// Сервис для управления автоматическим демпером цен

import { API_URL, API_BASE_PATH } from '@/config';
import { API_ENDPOINTS, buildApiUrl } from '@/config/api';

export interface DemperConfig {
  store_id: string;
  min_profit_percent: number;
  max_profit_percent: number;
  price_reduction_step: number;
  check_interval: number;
  max_concurrent_products: number;
  enabled: boolean;
}

export interface DemperStatus {
  store_id: string;
  status: 'stopped' | 'running' | 'paused' | 'error';
  config: DemperConfig | null;
  is_running: boolean;
  last_update: string;
}

export interface DemperStatistics {
  store_id: string;
  total_products: number;
  active_products: number;
  avg_price: number;
  min_price: number;
  max_price: number;
  last_update: string;
}

export interface DemperHealth {
  status: 'healthy' | 'degraded' | 'warning' | 'critical';
  total_stores: number;
  running_dempers: number;
  error_dempers: number;
  timestamp: string;
}

class DemperService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = `${API_URL}${API_BASE_PATH}`;
  }

  /**
   * Запустить демпер для магазина
   */
  async startDemper(config: DemperConfig): Promise<{ success: boolean; message: string; store_id: string }> {
    try {
      const response = await fetch(buildApiUrl(API_ENDPOINTS.demper.start), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(config),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Ошибка запуска демпера');
      }

      return await response.json();
    } catch (error) {
      console.error('Error starting demper:', error);
      throw error;
    }
  }

  /**
   * Остановить демпер для магазина
   */
  async stopDemper(storeId: string): Promise<{ success: boolean; message: string; store_id: string }> {
    try {
      const response = await fetch(buildApiUrl(API_ENDPOINTS.demper.stop), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ store_id: storeId }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Ошибка остановки демпера');
      }

      return await response.json();
    } catch (error) {
      console.error('Error stopping demper:', error);
      throw error;
    }
  }

  /**
   * Приостановить демпер
   */
  async pauseDemper(storeId: string): Promise<{ success: boolean; message: string; store_id: string }> {
    try {
      const response = await fetch(buildApiUrl(API_ENDPOINTS.demper.pause), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ store_id: storeId }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Ошибка приостановки демпера');
      }

      return await response.json();
    } catch (error) {
      console.error('Error pausing demper:', error);
      throw error;
    }
  }

  /**
   * Возобновить демпер
   */
  async resumeDemper(storeId: string): Promise<{ success: boolean; message: string; store_id: string }> {
    try {
      const response = await fetch(buildApiUrl(API_ENDPOINTS.demper.resume), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ store_id: storeId }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Ошибка возобновления демпера');
      }

      return await response.json();
    } catch (error) {
      console.error('Error resuming demper:', error);
      throw error;
    }
  }

  /**
   * Получить статус демпера
   */
  async getDemperStatus(storeId: string): Promise<DemperStatus> {
    try {
      const response = await fetch(buildApiUrl(API_ENDPOINTS.demper.status(storeId)));

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Ошибка получения статуса демпера');
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting demper status:', error);
      throw error;
    }
  }

  /**
   * Получить статистику демпера
   */
  async getDemperStatistics(storeId: string): Promise<DemperStatistics> {
    try {
      const response = await fetch(buildApiUrl(API_ENDPOINTS.demper.statistics(storeId)));

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Ошибка получения статистики демпера');
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting demper statistics:', error);
      throw error;
    }
  }

  /**
   * Получить список всех демперов
   */
  async listDempers(): Promise<DemperStatus[]> {
    try {
      const response = await fetch(buildApiUrl(API_ENDPOINTS.demper.list));

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Ошибка получения списка демперов');
      }

      return await response.json();
    } catch (error) {
      console.error('Error listing dempers:', error);
      throw error;
    }
  }

  /**
   * Остановить все демперы
   */
  async stopAllDempers(): Promise<{ success: boolean; message: string }> {
    try {
      const response = await fetch(buildApiUrl(API_ENDPOINTS.demper.stopAll), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Ошибка остановки всех демперов');
      }

      return await response.json();
    } catch (error) {
      console.error('Error stopping all dempers:', error);
      throw error;
    }
  }

  /**
   * Проверка здоровья системы демпера
   */
  async getDemperHealth(): Promise<DemperHealth> {
    try {
      const response = await fetch(buildApiUrl(API_ENDPOINTS.demper.health));

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Ошибка проверки здоровья демпера');
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting demper health:', error);
      throw error;
    }
  }

  /**
   * Создать конфигурацию демпера с настройками по умолчанию
   */
  createDefaultConfig(storeId: string): DemperConfig {
    return {
      store_id: storeId,
      min_profit_percent: 10.0,
      max_profit_percent: 40.0,
      price_reduction_step: 2.0,
      check_interval: 600, // 10 минут
      max_concurrent_products: 5,
      enabled: true,
    };
  }

  /**
   * Валидация конфигурации демпера
   */
  validateConfig(config: DemperConfig): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (!config.store_id) {
      errors.push('ID магазина обязателен');
    }

    if (config.min_profit_percent < 0 || config.min_profit_percent > 100) {
      errors.push('Минимальный процент прибыли должен быть от 0 до 100');
    }

    if (config.max_profit_percent < 0 || config.max_profit_percent > 100) {
      errors.push('Максимальный процент прибыли должен быть от 0 до 100');
    }

    if (config.min_profit_percent >= config.max_profit_percent) {
      errors.push('Минимальный процент прибыли должен быть меньше максимального');
    }

    if (config.price_reduction_step <= 0) {
      errors.push('Шаг снижения цены должен быть больше 0');
    }

    if (config.check_interval < 60) {
      errors.push('Интервал проверки должен быть не менее 60 секунд');
    }

    if (config.max_concurrent_products < 1) {
      errors.push('Максимальное количество товаров должно быть не менее 1');
    }

    return {
      valid: errors.length === 0,
      errors,
    };
  }
}

export const demperService = new DemperService();
export default demperService;
