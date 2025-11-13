// hooks/useSalesData.ts
import { useState, useEffect, useCallback, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { salesService, SalesData, SalesOrder, SalesProduct, SalesMetrics } from '@/services/salesService';
import { mockSalesData } from '@/data/mockData';
import { toast } from 'sonner';

interface UseSalesDataOptions {
  storeId: string | null;
  maxOrders?: number;
  enableAutoRefresh?: boolean;
  refreshInterval?: number;
  useBulkLoading?: boolean;
}

interface UseSalesDataReturn {
  // Данные
  orders: SalesOrder[];
  topProducts: SalesProduct[];
  metrics: SalesMetrics;
  chartData: Array<{ date: string; orders: number; revenue: number }>;
  
  // Состояние загрузки
  isLoading: boolean;
  error: string | null;
  hasRealData: boolean;
  bulkInfo?: {
    total_fetched: number;
    max_requested: number;
    pages_fetched: number;
    unique_products: number;
  };
  
  // Функции управления
  refetch: () => void;
  loadMoreData: (additionalOrders: number) => Promise<void>;
  resetData: () => void;
  
  // Фильтрация и поиск
  filteredOrders: SalesOrder[];
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  dateRange: { from?: Date; to?: Date };
  setDateRange: (range: { from?: Date; to?: Date }) => void;
}

export function useSalesData({
  storeId,
  maxOrders = 1000,
  enableAutoRefresh = false,
  refreshInterval = 5 * 60 * 1000, // 5 минут
  useBulkLoading = false
}: UseSalesDataOptions): UseSalesDataReturn {
  const [searchQuery, setSearchQuery] = useState('');
  const [dateRange, setDateRange] = useState<{ from?: Date; to?: Date }>({});
  const [additionalData, setAdditionalData] = useState<SalesData | null>(null);

  // Основной запрос данных
  const {
    data: salesData,
    isLoading,
    error: queryError,
    refetch
  } = useQuery({
    queryKey: ['salesData', storeId, maxOrders, useBulkLoading],
    queryFn: async () => {
      if (!storeId) {
        return {
          orders: [],
          top_products: [],
          metrics: {}
        };
      }

      try {
        let response;
        if (useBulkLoading || maxOrders > 1000) {
          response = await salesService.getSalesDataBulk(storeId, maxOrders);
        } else {
          response = await salesService.getSalesDataOptimized(storeId, maxOrders);
        }

        if (!response.success) {
          throw new Error(response.error || 'Failed to fetch sales data');
        }

        return response.data;
      } catch (error) {
        console.error('Error fetching sales data:', error);
        // Возвращаем пустые данные в случае ошибки
        return {
          orders: [],
          top_products: [],
          metrics: {}
        };
      }
    },
    enabled: !!storeId, // Включаем только если есть storeId
    staleTime: enableAutoRefresh ? refreshInterval : 10 * 60 * 1000, // 10 минут по умолчанию
    refetchInterval: enableAutoRefresh ? refreshInterval : false,
    retry: 1
  });

  // Объединение основных данных с дополнительными
  const combinedData = useMemo(() => {
    if (!salesData) return null;

    if (!additionalData) return salesData;

    // Объединяем данные
    const combinedOrders = [...salesData.orders, ...additionalData.orders];
    const combinedProducts = [...salesData.top_products, ...additionalData.top_products];
    
    // Удаляем дубликаты продуктов
    const uniqueProducts = combinedProducts.filter((product, index, self) => 
      index === self.findIndex(p => 
        (p.name || p.product_name) === (product.name || product.product_name)
      )
    );

    return {
      orders: combinedOrders,
      top_products: uniqueProducts,
      metrics: salesService.calculateMetrics(combinedOrders),
      bulk_info: additionalData.bulk_info || salesData.bulk_info
    };
  }, [salesData, additionalData]);

  // Фильтрация заказов по поисковому запросу и дате
  const filteredOrders = useMemo(() => {
    if (!combinedData) return [];

    let filtered = combinedData.orders;

    // Фильтрация по дате
    if (dateRange.from || dateRange.to) {
      filtered = filtered.filter(order => {
        const orderDate = new Date(order.date);
        
        if (dateRange.from && orderDate < dateRange.from) return false;
        if (dateRange.to && orderDate > dateRange.to) return false;
        
        return true;
      });
    }

    // Фильтрация по поисковому запросу (пока нет поиска по заказам)
    if (searchQuery) {
      // В будущем можно добавить поиск по номеру заказа или другим полям
      // filtered = filtered.filter(order => order.orderNumber?.includes(searchQuery));
    }

    return filtered;
  }, [combinedData, searchQuery, dateRange]);

  // Загрузка дополнительных данных
  const loadMoreData = useCallback(async (additionalOrders: number) => {
    if (!storeId) {
      toast.error('Магазин не выбран');
      return;
    }

    try {
      toast.info('Загружаю дополнительные данные...');
      
      const response = await salesService.getSalesDataBulk(storeId, additionalOrders);
      
      if (!response.success) {
        throw new Error(response.error || 'Failed to load additional data');
      }

      setAdditionalData(response.data);
      toast.success(`Загружено дополнительно: ${response.data.orders.length} заказов`);
    } catch (error) {
      console.error('Error loading additional data:', error);
      toast.error('Ошибка загрузки дополнительных данных');
    }
  }, [storeId]);

  // Сброс дополнительных данных
  const resetData = useCallback(() => {
    setAdditionalData(null);
    setSearchQuery('');
    setDateRange({});
  }, []);

  // Обработка ошибок
  const error = queryError ? (queryError as Error).message : null;

  // Показать уведомление при ошибке
  useEffect(() => {
    if (error && storeId) {
      toast.error(`Ошибка загрузки данных продаж: ${error}`);
    }
  }, [error, storeId]);

  return {
    // Данные
    orders: combinedData?.orders || [],
    topProducts: combinedData?.top_products || [],
    metrics: combinedData?.metrics || {},
    chartData: combinedData ? salesService.formatDataForCharts(combinedData.orders) : [],
    
    // Состояние загрузки
    isLoading,
    error,
    hasRealData: combinedData ? salesService.hasRealData(combinedData) : false,
    bulkInfo: combinedData?.bulk_info,
    
    // Функции управления
    refetch,
    loadMoreData,
    resetData,
    
    // Фильтрация и поиск
    filteredOrders,
    searchQuery,
    setSearchQuery,
    dateRange,
    setDateRange
  };
}
