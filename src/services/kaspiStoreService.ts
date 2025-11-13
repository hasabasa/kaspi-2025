import { API_URL, API_BASE_PATH } from "@/config";
import { API_ENDPOINTS, buildApiUrl } from "@/config/api";

export interface StoreConnectionData {
  session_id?: string;
  user_id?: string;
  email: string;
  password: string;
}

export interface KaspiStoreData {
  id: string;
  name: string;
  merchant_id: string;
  user_id?: string;
  session_id?: string;
  email: string;
  is_active: boolean;
  products_count: number;
  last_sync: string;
  created_at: string;
  updated_at: string;
  total_sales?: number;
  commission_percent?: number;
}

export interface SalesData {
  date: string;
  orders: number;
  revenue: number;
  items_sold: number;
  count: number;
  amount: number;
  store_id: string;
}

export interface Product {
  id: string;
  article: string;
  name: string;
  brand: string;
  price: number;
  stock: number;
  category: string;
  bot_enabled: boolean;
  min_price?: number;
  max_price?: number;
  price_step?: number;
  current_position?: number;
  target_position?: number;
  last_price_change?: string;
  store_id: string;
  image?: string;
}

class KaspiStoreService {
  private baseUrl = `${API_URL}${API_BASE_PATH}`;

  // Подключение магазина без авторизации (через сессию)
  async connectStoreSimple(data: StoreConnectionData): Promise<KaspiStoreData> {
    const response = await fetch(buildApiUrl(API_ENDPOINTS.kaspi.auth), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Ошибка подключения магазина');
    }

    return await response.json();
  }

  // Подключение магазина с авторизацией
  async connectStore(data: StoreConnectionData): Promise<KaspiStoreData> {
    const response = await fetch(buildApiUrl(API_ENDPOINTS.kaspi.auth), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Ошибка подключения магазина');
    }

    return await response.json();
  }

  // Получение данных продаж
  async getSalesData(storeId: string, dateFrom?: string, dateTo?: string): Promise<SalesData[]> {
    const params = new URLSearchParams();
    params.append('store_id', storeId);
    if (dateFrom) params.append('date_from', dateFrom);
    if (dateTo) params.append('date_to', dateTo);

    const response = await fetch(buildApiUrl(API_ENDPOINTS.sales.get) + `?${params.toString()}`);
    
    if (!response.ok) {
      throw new Error('Ошибка получения данных продаж');
    }

    return await response.json();
  }

  // Получение списка товаров
  async getProducts(storeId: string): Promise<Product[]> {
    const response = await fetch(buildApiUrl(API_ENDPOINTS.products.list) + `?store_id=${storeId}`);
    
    if (!response.ok) {
      throw new Error('Ошибка получения списка товаров');
    }

    return await response.json();
  }

  // Массовое обновление настроек прайс-бота
  async bulkUpdateBotSettings(data: {
    store_id: string;
    product_ids: string[];
    settings: {
      bot_enabled?: boolean;
      min_price?: number;
      max_price?: number;
      price_step?: number;
    };
  }): Promise<{ updated_count: number }> {
    const response = await fetch(buildApiUrl(API_ENDPOINTS.products.bulkUpdate), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Ошибка массового обновления товаров');
    }

    return await response.json();
  }

  // Поиск товаров
  async searchProducts(storeId: string, query: string, filters?: {
    bot_status?: 'enabled' | 'disabled';
    category?: string;
  }): Promise<Product[]> {
    const params = new URLSearchParams();
    params.append('store_id', storeId);
    params.append('query', query);
    
    if (filters?.bot_status) {
      params.append('bot_status', filters.bot_status);
    }
    if (filters?.category) {
      params.append('category', filters.category);
    }

    const response = await fetch(buildApiUrl(API_ENDPOINTS.products.search) + `?${params.toString()}`);
    
    if (!response.ok) {
      throw new Error('Ошибка поиска товаров');
    }

    return await response.json();
  }

  // Синхронизация товаров
  async syncProducts(storeId: string): Promise<{ synced_count: number }> {
    const response = await fetch(buildApiUrl(API_ENDPOINTS.kaspi.syncStore(storeId)), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ store_id: storeId }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Ошибка синхронизации товаров');
    }

    return await response.json();
  }
}

export const kaspiStoreService = new KaspiStoreService();
export default kaspiStoreService;
