import React, { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Info, Bot, RefreshCw, Settings } from "lucide-react";
import { useStoreContext } from "@/contexts/StoreContext";
import { useStoreConnection } from "@/hooks/useStoreConnection";
import LoadingScreen from "@/components/ui/loading-screen";
import { toast } from 'sonner';

// Новые компоненты
import BulkActionsPanel from "@/components/price-bot/BulkActionsPanel";
import ProductFilters, { ProductFilters as FilterType } from "@/components/price-bot/ProductFilters";
import ProductTable from "@/components/price-bot/ProductTable";

// Сервисы
import kaspiStoreService, { Product } from "@/services/kaspiStoreService";

const PriceBotPageNew = () => {
  const { selectedStoreId, selectedStore } = useStoreContext();
  const { isConnected, needsConnection, loading: storeLoading } = useStoreConnection();
  
  // Состояния
  const [products, setProducts] = useState<Product[]>([]);
  const [filteredProducts, setFilteredProducts] = useState<Product[]>([]);
  const [selectedProducts, setSelectedProducts] = useState<string[]>([]);
  const [loadingProducts, setLoadingProducts] = useState(false);
  const [syncing, setSyncing] = useState(false);
  
  // Фильтры
  const [filters, setFilters] = useState<FilterType>({
    search: '',
    botStatus: 'all',
    category: '',
    priceRange: { min: '', max: '' }
  });

  // Категории для фильтра
  const [categories, setCategories] = useState<string[]>([]);

  // Загрузка товаров
  const loadProducts = async () => {
    if (!selectedStoreId) return;

    setLoadingProducts(true);
    try {
      const productsData = await kaspiStoreService.getProducts(selectedStoreId);
      setProducts(productsData);
      
      // Извлекаем уникальные категории
      const uniqueCategories = [...new Set(productsData.map(p => p.category))].filter(Boolean);
      setCategories(uniqueCategories);
      
    } catch (error: any) {
      console.error('Error loading products:', error);
      toast.error('Ошибка загрузки товаров: ' + error.message);
      
      // В случае ошибки показываем демо-данные
      const demoProducts: Product[] = [
        {
          id: 'demo-1',
          article: 'PHONE001',
          name: 'iPhone 15 Pro Max 256GB',
          brand: 'Apple',
          price: 650000,
          stock: 5,
          category: 'Смартфоны',
          bot_enabled: true,
          min_price: 600000,
          max_price: 700000,
          price_step: 5000,
          current_position: 3,
          target_position: 1,
          store_id: selectedStoreId
        },
        {
          id: 'demo-2',
          article: 'PHONE002',
          name: 'Samsung Galaxy S24 Ultra',
          brand: 'Samsung',
          price: 580000,
          stock: 8,
          category: 'Смартфоны',
          bot_enabled: false,
          min_price: 550000,
          max_price: 620000,
          price_step: 3000,
          current_position: 7,
          target_position: 3,
          store_id: selectedStoreId
        },
        {
          id: 'demo-3',
          article: 'LAPTOP001',
          name: 'MacBook Air M2 13"',
          brand: 'Apple',
          price: 590000,
          stock: 2,
          category: 'Ноутбуки',
          bot_enabled: true,
          min_price: 570000,
          max_price: 610000,
          price_step: 2000,
          current_position: 5,
          target_position: 2,
          store_id: selectedStoreId
        }
      ];
      
      setProducts(demoProducts);
      setCategories(['Смартфоны', 'Ноутбуки']);
      
    } finally {
      setLoadingProducts(false);
    }
  };

  // Синхронизация товаров
  const handleSync = async () => {
    if (!selectedStoreId) return;

    setSyncing(true);
    try {
      const result = await kaspiStoreService.syncProducts(selectedStoreId);
      toast.success(`Синхронизировано ${result.synced_count} товаров`);
      await loadProducts(); // Перезагружаем список
    } catch (error: any) {
      console.error('Error syncing products:', error);
      toast.error('Ошибка синхронизации: ' + error.message);
    } finally {
      setSyncing(false);
    }
  };

  // Обновление товара
  const handleProductUpdate = async (productId: string, updates: Partial<Product>) => {
    try {
      // Обновляем товар через API
      await kaspiStoreService.bulkUpdateBotSettings({
        store_id: selectedStoreId!,
        product_ids: [productId],
        settings: updates
      });

      // Обновляем локальное состояние
      setProducts(prev => prev.map(p => 
        p.id === productId ? { ...p, ...updates } : p
      ));

    } catch (error: any) {
      console.error('Error updating product:', error);
      toast.error('Ошибка обновления товара: ' + error.message);
    }
  };

  // Фильтрация товаров
  useEffect(() => {
    let filtered = [...products];

    // Поиск по SKU или названию
    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      filtered = filtered.filter(p => 
        p.article.toLowerCase().includes(searchLower) ||
        p.name.toLowerCase().includes(searchLower)
      );
    }

    // Фильтр по статусу бота
    if (filters.botStatus !== 'all') {
      filtered = filtered.filter(p => 
        filters.botStatus === 'enabled' ? p.bot_enabled : !p.bot_enabled
      );
    }

    // Фильтр по категории
    if (filters.category) {
      filtered = filtered.filter(p => p.category === filters.category);
    }

    // Фильтр по диапазону цен
    if (filters.priceRange.min) {
      const minPrice = parseFloat(filters.priceRange.min);
      if (!isNaN(minPrice)) {
        filtered = filtered.filter(p => p.price >= minPrice);
      }
    }
    if (filters.priceRange.max) {
      const maxPrice = parseFloat(filters.priceRange.max);
      if (!isNaN(maxPrice)) {
        filtered = filtered.filter(p => p.price <= maxPrice);
      }
    }

    setFilteredProducts(filtered);
  }, [products, filters]);

  // Загрузка товаров при смене магазина
  useEffect(() => {
    if (selectedStoreId) {
      loadProducts();
    }
  }, [selectedStoreId]);

  // Сброс выбранных товаров при смене фильтров
  useEffect(() => {
    setSelectedProducts([]);
  }, [filters]);

  // Показываем загрузку если магазины загружаются
  if (storeLoading) {
    return <LoadingScreen text="Загрузка данных магазинов..." />;
  }

  // Временно скрываем проверку подключения для демонстрации
  // if (needsConnection) { ... }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Заголовок */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">Прайс-бот</h1>
          <p className="text-muted-foreground text-sm md:text-base">
            Автоматическое управление ценами для победы в конкурентной борьбе
          </p>
        </div>
        
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            onClick={handleSync}
            disabled={syncing || !selectedStoreId}
            className="flex items-center gap-2"
          >
            <RefreshCw className={`h-4 w-4 ${syncing ? 'animate-spin' : ''}`} />
            {syncing ? 'Синхронизация...' : 'Синхронизировать'}
          </Button>
          
          {selectedStore && (
            <div className="text-sm text-muted-foreground">
              Магазин: <span className="font-medium">{selectedStore.name}</span>
            </div>
          )}
        </div>
      </div>

      {/* Информационное сообщение */}
      <Alert className="bg-primary/5 border-primary/20">
        <Info className="h-4 w-4 text-primary flex-shrink-0" />
        <AlertDescription className="text-primary text-xs md:text-sm">
          Прайс-бот автоматически анализирует цены конкурентов и корректирует ваши цены для удержания топовых позиций.
        </AlertDescription>
      </Alert>

      {/* Массовые действия */}
      <BulkActionsPanel
        selectedProducts={selectedProducts}
        storeId={selectedStoreId || ''}
        onUpdate={loadProducts}
        totalProducts={filteredProducts.length}
      />

      {/* Фильтры */}
      <ProductFilters
        filters={filters}
        onFiltersChange={setFilters}
        categories={categories}
        resultCount={filteredProducts.length}
      />

      {/* Таблица товаров */}
      <ProductTable
        products={filteredProducts}
        selectedProducts={selectedProducts}
        onSelectionChange={setSelectedProducts}
        onProductUpdate={handleProductUpdate}
        isLoading={loadingProducts}
      />

      {/* Статистика */}
      {products.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Всего товаров</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{products.length}</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Бот активен</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {products.filter(p => p.bot_enabled).length}
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Бот неактивен</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">
                {products.filter(p => !p.bot_enabled).length}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default PriceBotPageNew;
