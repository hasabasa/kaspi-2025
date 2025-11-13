// services/salesService.ts
import { API_URL, API_BASE_PATH } from '@/config';
import { API_ENDPOINTS, buildApiUrl } from '@/config/api';
interface SalesOrder {
  date: string;
  count: number;
  amount: number;
}

interface SalesProduct {
  name?: string;
  product_name?: string;
  quantity?: number;
  amount?: number;
}

interface SalesMetrics {
  totalRevenue?: number;
  totalOrders?: number;
  avgOrderValue?: number;
  itemsSold?: number;
}

interface PaginationInfo {
  page: number;
  page_size: number;
  total_fetched: number;
  has_more: boolean;
  start_index: number;
}

interface BulkInfo {
  total_fetched: number;
  max_requested: number;
  pages_fetched: number;
  unique_products: number;
}

interface SalesData {
  orders: SalesOrder[];
  top_products: SalesProduct[];
  metrics: SalesMetrics;
  pagination?: PaginationInfo;
  bulk_info?: BulkInfo;
}

interface SalesResponse {
  success: boolean;
  data: SalesData;
  error?: string;
}

class SalesService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = `${API_URL}${API_BASE_PATH}`;
  }

  /**
   * Получает данные о продажах с пагинацией
   */
  async getSalesData(
    storeId: string,
    page: number = 0,
    pageSize: number = 500
  ): Promise<SalesResponse> {
    try {
      const url = buildApiUrl(API_ENDPOINTS.sales.get) + `?store_id=${storeId}&page=${page}&page_size=${pageSize}`;
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const salesArray = await response.json();
      
      // Преобразуем массив продаж в формат, ожидаемый фронтендом
      const orders: SalesOrder[] = salesArray.map((sale: any) => ({
        date: sale.order_date,
        count: sale.quantity,
        amount: sale.total_amount,
        store_id: sale.store_id
      }));

      const topProducts: SalesProduct[] = salesArray.map((sale: any) => ({
        name: sale.product_name,
        product_name: sale.product_name,
        quantity: sale.quantity,
        amount: sale.total_amount
      }));

      const metrics = this.calculateMetrics(orders);

      return {
        success: true,
        data: {
          orders,
          top_products: topProducts,
          metrics,
          pagination: {
            page,
            page_size: pageSize,
            total_fetched: salesArray.length,
            has_more: salesArray.length === pageSize,
            start_index: page * pageSize
          }
        }
      };
    } catch (error) {
      console.error('Error fetching sales data:', error);
      return {
        success: false,
        data: {
          orders: [],
          top_products: [],
          metrics: {}
        },
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  /**
   * Получает все доступные данные о продажах (массовая загрузка)
   */
  async getSalesDataBulk(
    storeId: string,
    maxOrders: number = 3000
  ): Promise<SalesResponse> {
    try {
      // Используем обычный метод с большим page_size
      return await this.getSalesData(storeId, 0, maxOrders);
    } catch (error) {
      console.error('Error fetching bulk sales data:', error);
      return {
        success: false,
        data: {
          orders: [],
          top_products: [],
          metrics: {}
        },
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  /**
   * Получает данные о продажах с автоматическим выбором метода загрузки
   * Использует bulk загрузку для больших объемов данных
   */
  async getSalesDataOptimized(
    storeId: string,
    maxOrders: number = 1000
  ): Promise<SalesResponse> {
    if (maxOrders > 1000) {
      // Для больших объемов используем bulk загрузку
      return this.getSalesDataBulk(storeId, maxOrders);
    } else {
      // Для небольших объемов используем обычную пагинацию
      return this.getSalesData(storeId, 0, maxOrders);
    }
  }

  /**
   * Агрегирует данные о продажах по дням
   */
  aggregateSalesByDate(orders: SalesOrder[]): Record<string, { count: number; amount: number }> {
    const aggregated: Record<string, { count: number; amount: number }> = {};

    orders.forEach(order => {
      const date = order.date.split('T')[0]; // Получаем только дату без времени
      
      if (!aggregated[date]) {
        aggregated[date] = { count: 0, amount: 0 };
      }
      
      aggregated[date].count += order.count;
      aggregated[date].amount += order.amount;
    });

    return aggregated;
  }

  /**
   * Вычисляет общие метрики из списка заказов
   */
  calculateMetrics(orders: SalesOrder[]): SalesMetrics {
    const totalOrders = orders.reduce((sum, order) => sum + order.count, 0);
    const totalRevenue = orders.reduce((sum, order) => sum + order.amount, 0);
    const avgOrderValue = totalOrders > 0 ? totalRevenue / totalOrders : 0;

    return {
      totalOrders,
      totalRevenue,
      avgOrderValue,
      itemsSold: totalOrders // Предполагаем, что количество заказов = количество проданных товаров
    };
  }

  /**
   * Фильтрует продукты по топ N
   */
  getTopProducts(products: SalesProduct[], limit: number = 10): SalesProduct[] {
    return products
      .sort((a, b) => (b.amount || 0) - (a.amount || 0))
      .slice(0, limit);
  }

  /**
   * Форматирует данные для графиков
   */
  formatDataForCharts(orders: SalesOrder[]): Array<{
    date: string;
    orders: number;
    revenue: number;
  }> {
    const aggregated = this.aggregateSalesByDate(orders);
    
    return Object.entries(aggregated)
      .map(([date, data]) => ({
        date,
        orders: data.count,
        revenue: data.amount
      }))
      .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
  }

  /**
   * Проверяет есть ли реальные данные (не моки)
   */
  hasRealData(data: SalesData): boolean {
    // Проверяем наличие pagination или bulk_info как индикатора реальных данных
    return !!(data.pagination || data.bulk_info);
  }
}

export const salesService = new SalesService();
export type { SalesData, SalesResponse, SalesOrder, SalesProduct, SalesMetrics };
