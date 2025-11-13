// pages/SalesPageEnhanced.tsx
import React, { useState, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { 
  BarChart3, 
  TrendingUp, 
  Package, 
  DollarSign,
  Download,
  RefreshCw,
  Settings,
  Zap,
  Info,
  Database,
  Clock
} from "lucide-react";
import { VirtualizedOrdersList } from "@/components/sales/VirtualizedOrdersList";
import { useSalesData } from "@/hooks/useSalesData";
import { useStoreContext } from "@/contexts/StoreContext";
import { useAuth } from "@/components/integration/useAuth";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
// Убираем мобильный хук для простоты
// import { useMobileOptimizedSimple as useMobileOptimized } from "@/hooks/useMobileOptimizedSimple";

const SalesPageEnhanced = () => {
  const { user, loading: authLoading } = useAuth();
  const { selectedStoreId, selectedStore } = useStoreContext();
  // Убираем мобильный хук
  // const mobile = useMobileOptimized();
  
  // Настройки загрузки данных
  const [maxOrders, setMaxOrders] = useState(1000);
  const [useBulkLoading, setUseBulkLoading] = useState(false);
  const [enableAutoRefresh, setEnableAutoRefresh] = useState(false);
  const [activeView, setActiveView] = useState("charts");

  // Хук для управления данными продаж
  const {
    orders,
    topProducts,
    metrics,
    chartData,
    isLoading,
    error,
    hasRealData,
    bulkInfo,
    refetch,
    loadMoreData,
    resetData,
    filteredOrders,
    searchQuery,
    setSearchQuery,
    dateRange,
    setDateRange
  } = useSalesData({
    storeId: selectedStoreId,
    maxOrders,
    enableAutoRefresh,
    useBulkLoading
  });

  // Обработчики действий
  const handleLoadMore = useCallback(async () => {
    const additionalOrders = maxOrders > 1000 ? 2000 : 1000;
    await loadMoreData(additionalOrders);
  }, [loadMoreData, maxOrders]);

  const handleExport = useCallback(() => {
    // Простой экспорт в CSV
    const csvData = filteredOrders.map(order => ({
      date: order.date,
      orders: order.count,
      revenue: order.amount
    }));
    
    const csv = [
      ['Дата', 'Заказы', 'Выручка'],
      ...csvData.map(row => [row.date, row.orders, row.revenue])
    ].map(row => row.join(',')).join('\n');
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `sales_data_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
    
    toast.success('Данные экспортированы в CSV');
  }, [filteredOrders]);

  const handleSettingsChange = useCallback((setting: string, value: any) => {
    switch (setting) {
      case 'maxOrders':
        setMaxOrders(value);
        break;
      case 'useBulkLoading':
        setUseBulkLoading(value);
        break;
      case 'enableAutoRefresh':
        setEnableAutoRefresh(value);
        break;
    }
  }, []);

  // Форматирование чисел
  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('ru-KZ').format(price) + ' ₸';
  };

  const formatFullPrice = (price: number) => {
    return formatPrice(price); // Показываем полную сумму без сокращений
  };



  return (
    <div className="animate-fade-in bg-background min-h-screen">
      <div className="container mx-auto p-4 md:p-6 space-y-4 md:space-y-6">
        {/* Заголовок */}
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="text-center md:text-left w-full md:w-auto">
            <h1 className="text-2xl md:text-3xl font-bold">
              Мои продажи
            </h1>
            <p className="text-sm md:text-base text-muted-foreground">
              Анализ продаж {selectedStore ? `магазина "${selectedStore.name}"` : 'всех магазинов'}
            </p>
          </div>
          
          {/* Убрали бейджи с информацией о данных */}
        </div>

        {/* Убрали настройки загрузки данных */}

        {/* Убрали информацию о производительности */}

        {/* Основные метрики */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card className="p-3 md:p-4">
            <div className="flex flex-col space-y-2">
              <div className="flex items-center gap-2">
                <span className="text-lg md:text-xl font-bold text-gray-600 dark:text-gray-400">₸</span>
                <p className="text-sm md:text-base font-medium text-gray-900 dark:text-white">Общая выручка</p>
              </div>
              <div className="text-lg md:text-2xl font-bold text-foreground">
                {formatFullPrice(metrics.totalRevenue || 0)}
              </div>
            </div>
          </Card>

          <Card className="p-4">
            <div className="flex flex-col space-y-2">
              <div className="flex items-center gap-2">
                <Package className="h-5 w-5 text-blue-500" />
                <p className="font-medium text-gray-900 dark:text-white">Заказы</p>
              </div>
              <div className="text-2xl font-bold text-foreground">
                {metrics.totalOrders || 0}
              </div>
            </div>
          </Card>

          <Card className="p-4">
            <div className="flex flex-col space-y-2">
              <div className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-green-500" />
                <p className="font-medium text-gray-900 dark:text-white">Товаров продано</p>
              </div>
              <div className="text-2xl font-bold text-foreground">
                {metrics.itemsSold || 0}
              </div>
            </div>
          </Card>

          <Card className="p-4">
            <div className="flex flex-col space-y-2">
              <div className="flex items-center gap-2">
                <span className="text-lg font-bold text-gray-600 dark:text-gray-400">₸</span>
                <p className="font-medium text-gray-900 dark:text-white">Средний чек</p>
              </div>
              <div className="text-2xl font-bold text-foreground">
                {formatFullPrice(metrics.avgOrderValue || 0)}
              </div>
            </div>
          </Card>
        </div>

        {/* Основной контент */}
        <Tabs value={activeView} onValueChange={setActiveView}>
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="charts" className="flex items-center gap-2">
              <BarChart3 className="h-4 w-4" />
              Графики
            </TabsTrigger>
            <TabsTrigger value="orders" className="flex items-center gap-2">
              <Package className="h-4 w-4" />
              Список заказов
            </TabsTrigger>
          </TabsList>

          <TabsContent value="charts" className="space-y-6 mt-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* График выручки */}
              <Card>
                <CardHeader>
                  <CardTitle>Динамика продаж</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-[300px] flex items-center justify-center text-muted-foreground">
                    <div className="text-center">
                      <BarChart3 className="h-12 w-12 mx-auto mb-2" />
                      <p>График будет добавлен</p>
                      <p className="text-sm">({chartData.length} точек данных)</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Топ товары */}
              <Card>
                <CardHeader>
                  <CardTitle>Топ товары</CardTitle>
                </CardHeader>
                <CardContent>
                  {topProducts.length > 0 ? (
                    <div className="space-y-2">
                      {topProducts.slice(0, 5).map((product, index) => (
                        <div key={index} className="flex items-center justify-between p-2 border rounded">
                          <span className="font-medium">
                            {product.name || product.product_name || `Товар ${index + 1}`}
                          </span>
                          <span className="text-sm text-muted-foreground">
                            {product.quantity || 0} шт.
                          </span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center text-muted-foreground py-8">
                      <Package className="h-8 w-8 mx-auto mb-2" />
                      <p>Нет данных о товарах</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="orders" className="mt-6">
            <VirtualizedOrdersList
              orders={filteredOrders}
              searchQuery={searchQuery}
              onSearchChange={setSearchQuery}
              onLoadMore={handleLoadMore}
              onRefresh={refetch}
              onExport={handleExport}
            />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default SalesPageEnhanced;
