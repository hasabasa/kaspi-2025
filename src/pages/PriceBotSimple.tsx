import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Checkbox } from "@/components/ui/checkbox";
import { SafeImage } from "@/components/ui/SafeImage";
import { API_URL, API_BASE_PATH } from "@/config";

import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Search, 
  Bot, 
  Power, 
  PowerOff, 
  DollarSign,
  Settings,
  CheckCircle2,
  Package,
  TrendingUp,
  Image,
  Users,
  Filter,
  Activity,
  Wifi
} from "lucide-react";
// Убрали WebSocket компоненты для демпера
import { useStoreConnection } from "@/hooks/use-store-connection";
import { toast } from 'sonner';
import { useStoreContext } from "@/contexts/StoreContext";
import kaspiStoreService, { Product } from "@/services/kaspiStoreService";
// Временно убираем мобильные импорты
// import { useMobileOptimizedSimple as useMobileOptimized } from "@/hooks/useMobileOptimizedSimple";
// import { MobilePriceBotCard } from "@/components/mobile/MobilePriceBotCard";

const PriceBotSimple = () => {
  // Функция для безопасной загрузки изображений
  const getSafeImageUrl = (imageUrl: string) => {
    if (!imageUrl) {
      return 'https://via.placeholder.com/200x200?text=No+Image';
    }
    
    // Если URL содержит resources.kaspi.kz, заменяем на placeholder
    if (imageUrl.includes('resources.kaspi.kz')) {
      return 'https://via.placeholder.com/200x200?text=Kaspi+Image';
    }
    
    return imageUrl;
  };
  const { selectedStoreId, selectedStore } = useStoreContext();
  // Временно убираем мобильный хук
  // const mobile = useMobileOptimized();
  
  // Убрали WebSocket подключение
  
  // Состояния
  const [products, setProducts] = useState<Product[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredProducts, setFilteredProducts] = useState<Product[]>([]);
  const [showBotOnly, setShowBotOnly] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  
  // Состояния для выбора товаров
  const [selectedProducts, setSelectedProducts] = useState<string[]>([]);
  const [viewMode, setViewMode] = useState<'all' | 'active' | 'inactive'>('all');
  
  // Состояния для настроек выбранных товаров
  const [bulkSettingsOpen, setBulkSettingsOpen] = useState(false);
  const [bulkSettings, setBulkSettings] = useState({
    minPrice: '',
    maxPrice: '', 
    priceStep: ''
  });

  // Состояния для быстрых настроек
  const [quickSettings, setQuickSettings] = useState({
    minPrice: '',
    maxPrice: '',
    priceStep: ''
  });

  // Демо товары
  const demoProducts: Product[] = [
    {
      id: '1',
      article: 'PHONE001',
      name: 'iPhone 15 Pro Max 256GB Титан',
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
      store_id: selectedStoreId || 'demo',
      image: 'https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=200&h=200&fit=crop&crop=center'
    },
    {
      id: '2',
      article: 'PHONE002',
      name: 'Samsung Galaxy S24 Ultra 512GB',
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
      store_id: selectedStoreId || 'demo',
      image: 'https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=200&h=200&fit=crop&crop=center'
    },
    {
      id: '3',
      article: 'LAPTOP001',
      name: 'MacBook Air M2 13" 256GB',
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
      store_id: selectedStoreId || 'demo',
      image: 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=200&h=200&fit=crop&crop=center'
    },
    {
      id: '4',
      article: 'WATCH001',
      name: 'Apple Watch Series 9 45mm',
      brand: 'Apple',
      price: 199000,
      stock: 12,
      category: 'Умные часы',
      bot_enabled: false,
      min_price: 180000,
      max_price: 220000,
      price_step: 1000,
      current_position: 8,
      target_position: 5,
      store_id: selectedStoreId || 'demo',
      image: 'https://images.unsplash.com/photo-1434494878577-86c23bcb06b9?w=200&h=200&fit=crop&crop=center'
    },
    {
      id: '5',
      article: 'TABLET001',
      name: 'iPad Air 5 256GB Wi-Fi',
      brand: 'Apple',
      price: 350000,
      stock: 6,
      category: 'Планшеты',
      bot_enabled: true,
      min_price: 330000,
      max_price: 370000,
      price_step: 2000,
      current_position: 2,
      target_position: 1,
      store_id: selectedStoreId || 'demo',
      image: 'https://images.unsplash.com/photo-1561154464-82e9adf32764?w=200&h=200&fit=crop&crop=center'
    }
  ];

  // Загрузка товаров
  useEffect(() => {
    loadProducts();
  }, [selectedStoreId]);

  const loadProducts = async () => {
    setIsLoading(true);
    try {
      // Получаем реальные товары из API
      const storeId = "2e236ced-c24b-4c55-bec7-dc56b8b5c174"; // Используем реальный store_id
      let url = `${API_URL}${API_BASE_PATH}/products/?store_id=${storeId}`;
      
      console.log('Loading products from URL:', url);
      
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      console.log('Loaded products response:', result);
      
      const productsData = result.items || [];
      
      // Преобразуем данные в нужный формат
      const formattedProducts = productsData.map((product: any) => ({
        id: product.id,
        article: product.kaspi_sku || '',
        name: product.name || '',
        price: product.price || 0,
        brand: product.brand || '',
        category: product.category || '',
        image: getSafeImageUrl(product.image_url),
        bot_enabled: product.bot_active || false,
        store_id: product.store_id || storeId,
        // Добавляем поля для прайс-бота
        min_price: product.min_price || 0,
        max_price: product.max_price || product.price || 0,
        price_step: product.price_step || 100,
        target_position: product.target_position || 1,
        current_position: product.current_position || 1,
        competitor_count: product.competitor_count || 0,
        last_updated: product.updated_at || new Date().toISOString()
      }));
      
      console.log('Formatted products:', formattedProducts);
      setProducts(formattedProducts);
      
    } catch (error) {
      console.error('Error loading products:', error);
      toast.error('Ошибка загрузки товаров');
      // Устанавливаем пустой массив вместо демо-данных
      setProducts([]);
    } finally {
      setIsLoading(false);
    }
  };

  // Фильтрация товаров
  useEffect(() => {
    let filtered = products;

    // Поиск
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(p => 
        p.name.toLowerCase().includes(query) ||
        p.article.toLowerCase().includes(query) ||
        p.brand.toLowerCase().includes(query)
      );
    }

    // Фильтр по режиму просмотра
    if (viewMode === 'active') {
      filtered = filtered.filter(p => p.bot_enabled);
    } else if (viewMode === 'inactive') {
      filtered = filtered.filter(p => !p.bot_enabled);
    }

    // Дополнительный фильтр "только с активным ботом"
    if (showBotOnly) {
      filtered = filtered.filter(p => p.bot_enabled);
    }

    setFilteredProducts(filtered);
  }, [products, searchQuery, showBotOnly, viewMode]);

  // Сброс выбранных товаров при смене режима просмотра
  useEffect(() => {
    setSelectedProducts([]);
  }, [viewMode]);

  // Включить/выключить бот для товара
  const toggleBot = async (productId: string, enabled: boolean) => {
    setProducts(prev => prev.map(p => 
      p.id === productId ? { ...p, bot_enabled: enabled } : p
    ));
    
    toast.success(
      enabled 
        ? `Прайс-бот включен` 
        : `Прайс-бот выключен`
    );
  };

  // Применить быстрые настройки ко всем товарам с включенным ботом
  const applyQuickSettings = () => {
    const enabledProducts = products.filter(p => p.bot_enabled);
    
    if (enabledProducts.length === 0) {
      toast.error('Сначала включите бот хотя бы для одного товара');
      return;
    }

    let hasChanges = false;
    const updates: any = {};

    if (quickSettings.minPrice) {
      const minPrice = parseFloat(quickSettings.minPrice);
      if (!isNaN(minPrice) && minPrice > 0) {
        updates.min_price = minPrice;
        hasChanges = true;
      }
    }

    if (quickSettings.maxPrice) {
      const maxPrice = parseFloat(quickSettings.maxPrice);
      if (!isNaN(maxPrice) && maxPrice > 0) {
        updates.max_price = maxPrice;
        hasChanges = true;
      }
    }

    if (quickSettings.priceStep) {
      const priceStep = parseFloat(quickSettings.priceStep);
      if (!isNaN(priceStep) && priceStep > 0) {
        updates.price_step = priceStep;
        hasChanges = true;
      }
    }

    if (!hasChanges) {
      toast.error('Введите хотя бы одно значение');
      return;
    }

    // Проверка соотношения цен
    if (updates.min_price && updates.max_price && updates.min_price >= updates.max_price) {
      toast.error('Минимальная цена должна быть меньше максимальной');
      return;
    }

    // Применяем настройки
    setProducts(prev => prev.map(p => 
      p.bot_enabled ? { ...p, ...updates } : p
    ));

    toast.success(`Настройки применены к ${enabledProducts.length} товарам`);
    
      // Очищаем поля
  setQuickSettings({ minPrice: '', maxPrice: '', priceStep: '' });
};

// Функции для работы с выбранными товарами
const handleSelectProduct = (productId: string, checked: boolean) => {
  if (checked) {
    setSelectedProducts(prev => [...prev, productId]);
  } else {
    setSelectedProducts(prev => prev.filter(id => id !== productId));
  }
};

const handleSelectAll = (checked: boolean) => {
  if (checked) {
    setSelectedProducts(filteredProducts.map(p => p.id));
  } else {
    setSelectedProducts([]);
  }
};

// Применить настройки к выбранным товарам
const applyBulkSettings = () => {
  if (selectedProducts.length === 0) {
    toast.error('Выберите товары для настройки');
    return;
  }
  
  // Проверяем, что все поля заполнены
  if (!bulkSettings.minPrice || !bulkSettings.maxPrice || !bulkSettings.priceStep) {
    toast.error('Заполните все поля');
    return;
  }
  
  const minPrice = parseFloat(bulkSettings.minPrice);
  const maxPrice = parseFloat(bulkSettings.maxPrice);
  const priceStep = parseFloat(bulkSettings.priceStep);
  
  // Проверяем корректность значений
  if (minPrice >= maxPrice) {
    toast.error('Минимальная цена должна быть меньше максимальной');
    return;
  }
  
  if (priceStep <= 0) {
    toast.error('Шаг изменения должен быть больше 0');
    return;
  }
  
  setProducts(prev => prev.map(p => {
    if (selectedProducts.includes(p.id)) {
      return {
        ...p,
        bot_enabled: true,
        min_margin: minPrice,
        max_margin: maxPrice,
        price_step: priceStep
      };
    }
    return p;
  }));

  toast.success(`Настройки применены к ${selectedProducts.length} товарам`);
  setSelectedProducts([]);
  setBulkSettingsOpen(false);
  // Очищаем поля
  setBulkSettings({
    minPrice: '',
    maxPrice: '', 
    priceStep: ''
  });
};



  // Включить бот для всех товаров
  const enableAllBots = () => {
    setProducts(prev => prev.map(p => ({ ...p, bot_enabled: true })));
    toast.success('Прайс-бот включен для всех товаров');
  };

  // Выключить бот для всех товаров
  const disableAllBots = () => {
    setProducts(prev => prev.map(p => ({ ...p, bot_enabled: false })));
    toast.success('Прайс-бот выключен для всех товаров');
  };

  // Убрали функции управления демпером

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('ru-KZ').format(price) + ' ₸';
  };

  const activeBotsCount = products.filter(p => p.bot_enabled).length;

  return (
    <div className="container mx-auto p-4 md:p-6 space-y-4 md:space-y-6">
      {/* Заголовок */}
      <div className="text-center md:text-left">
        <h1 className="text-2xl md:text-3xl font-bold mb-2">
          Прайс-бот
        </h1>
        <p className="text-sm md:text-base text-muted-foreground">
          Простое управление ценами на ваши товары
        </p>
      </div>

      {/* Статистика */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-3 md:p-4">
            <div className="flex items-center gap-2 md:gap-3">
              <Package className="h-6 w-6 md:h-8 md:w-8 text-blue-500" />
              <div>
                <div className="text-xl md:text-2xl font-bold">{products.length}</div>
                <div className="text-xs md:text-sm text-muted-foreground">Всего товаров</div>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-3 md:p-4">
            <div className="flex items-center gap-2 md:gap-3">
              <Power className="h-6 w-6 md:h-8 md:w-8 text-green-500" />
              <div>
                <div className="text-xl md:text-2xl font-bold text-green-600">{activeBotsCount}</div>
                <div className="text-xs md:text-sm text-muted-foreground">Бот активен</div>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-3 md:p-4">
            <div className="flex items-center gap-2 md:gap-3">
              <PowerOff className="h-6 w-6 md:h-8 md:w-8 text-red-500" />
              <div>
                <div className="text-xl md:text-2xl font-bold text-red-600">{products.length - activeBotsCount}</div>
                <div className="text-xs md:text-sm text-muted-foreground">Бот неактивен</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Убрали статус демпера и активность */}

      {/* Быстрые действия */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            Быстрые действия
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4 p-3 md:p-6">
          {/* Управление ботом */}
          <div className="flex flex-col sm:flex-row gap-2">
            <Button onClick={enableAllBots} className="flex items-center justify-center gap-2 text-sm">
              <Power className="h-4 w-4" />
              Включить бот для всех
            </Button>
            <Button 
              variant="outline" 
              onClick={disableAllBots}
              className="flex items-center justify-center gap-2 text-sm"
            >
              <PowerOff className="h-4 w-4" />
              Выключить бот для всех
            </Button>
          </div>

          {/* Быстрые настройки цен */}
          <div className="border-t pt-4">
            <h4 className="font-medium mb-3 text-sm md:text-base">Настройки цен для товаров с активным ботом</h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
              <div>
                <label className="text-sm text-muted-foreground">Мин. цена (₸)</label>
                <Input
                  type="number"
                  placeholder="100000"
                  value={quickSettings.minPrice}
                  onChange={(e) => setQuickSettings(prev => ({ ...prev, minPrice: e.target.value }))}
                />
              </div>
              <div>
                <label className="text-sm text-muted-foreground">Макс. цена (₸)</label>
                <Input
                  type="number"
                  placeholder="200000"
                  value={quickSettings.maxPrice}
                  onChange={(e) => setQuickSettings(prev => ({ ...prev, maxPrice: e.target.value }))}
                />
              </div>
              <div>
                <label className="text-sm text-muted-foreground">Шаг (₸)</label>
                <Input
                  type="number"
                  placeholder="1000"
                  value={quickSettings.priceStep}
                  onChange={(e) => setQuickSettings(prev => ({ ...prev, priceStep: e.target.value }))}
                />
              </div>
              <div className="flex items-end">
                <Button onClick={applyQuickSettings} className="w-full">
                  <CheckCircle2 className="h-4 w-4 mr-2" />
                  Применить
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Поиск и фильтры */}
      <Card>
        <CardContent className="p-3 md:p-4">
          <div className="space-y-4">
            <div className="flex flex-col gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
                <Input
                  placeholder="Поиск по названию, SKU или бренду..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 text-sm md:text-base"
                />
              </div>
              <div className="flex items-center gap-2">
                <Switch
                  checked={showBotOnly}
                  onCheckedChange={setShowBotOnly}
                />
                <span className="text-xs md:text-sm">Только с активным ботом</span>
              </div>
            </div>

            {/* Табы для просмотра товаров */}
            <Tabs value={viewMode} onValueChange={(value) => setViewMode(value as any)}>
              <TabsList className="grid w-full grid-cols-3 h-auto">
                <TabsTrigger value="all" className="flex items-center gap-1 md:gap-2 text-xs md:text-sm py-2">
                  <Package className="h-3 w-3 md:h-4 md:w-4" />
                  <span className="hidden sm:inline">Все товары</span>
                  <span className="sm:hidden">Все</span>
                </TabsTrigger>
                <TabsTrigger value="active" className="flex items-center gap-1 md:gap-2 text-xs md:text-sm py-2">
                  <Power className="h-3 w-3 md:h-4 md:w-4" />
                  <span className="hidden sm:inline">Активные</span>
                  <span className="sm:hidden">Акт.</span>
                </TabsTrigger>
                <TabsTrigger value="inactive" className="flex items-center gap-1 md:gap-2 text-xs md:text-sm py-2">
                  <PowerOff className="h-3 w-3 md:h-4 md:w-4" />
                  <span className="hidden sm:inline">Неактивные</span>
                  <span className="sm:hidden">Неакт.</span>
                </TabsTrigger>
              </TabsList>
            </Tabs>

            {/* Действия с выбранными товарами */}
            {selectedProducts.length > 0 && (
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between p-3 bg-primary/5 rounded-lg border border-primary/20 gap-3">
                <div className="flex items-center gap-2">
                  <Users className="h-4 w-4 text-primary" />
                  <span className="text-sm text-primary">
                    Выбрано товаров: {selectedProducts.length}
                  </span>
                </div>
                <div className="flex items-center gap-2 w-full sm:w-auto">
                  <Dialog open={bulkSettingsOpen} onOpenChange={setBulkSettingsOpen}>
                    <DialogTrigger asChild>
                      <Button size="sm" className="flex items-center gap-2 text-xs md:text-sm flex-1 sm:flex-none">
                        <Settings className="h-3 w-3 md:h-4 md:w-4" />
                        <span className="hidden sm:inline">Настроить стратегию</span>
                        <span className="sm:hidden">Настроить</span>
                      </Button>
                    </DialogTrigger>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>Настройка стратегии для выбранных товаров</DialogTitle>
                      </DialogHeader>
                      <div className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <Label htmlFor="bulk-min-price">Минимальная цена (₸)</Label>
                            <Input
                              id="bulk-min-price"
                              type="number"
                              placeholder="50000"
                              value={bulkSettings.minPrice}
                              onChange={(e) => setBulkSettings(prev => ({ ...prev, minPrice: e.target.value }))}
                            />
                          </div>
                          <div>
                            <Label htmlFor="bulk-max-price">Максимальная цена (₸)</Label>
                            <Input
                              id="bulk-max-price"
                              type="number"
                              placeholder="200000"
                              value={bulkSettings.maxPrice}
                              onChange={(e) => setBulkSettings(prev => ({ ...prev, maxPrice: e.target.value }))}
                            />
                          </div>
                        </div>
                        
                        <div>
                          <Label htmlFor="bulk-price-step">Шаг изменения цены (₸)</Label>
                          <Input
                            id="bulk-price-step"
                            type="number"
                            placeholder="1000"
                            value={bulkSettings.priceStep}
                            onChange={(e) => setBulkSettings(prev => ({ ...prev, priceStep: e.target.value }))}
                          />
                          <p className="text-xs text-muted-foreground mt-1">
                            На сколько тенге изменять цену при корректировке
                          </p>
                        </div>

                        <div className="text-sm text-muted-foreground">
                          Будет применено к {selectedProducts.length} товарам
                        </div>

                        <div className="flex gap-2">
                          <Button onClick={applyBulkSettings} className="flex-1">
                            Применить настройки
                          </Button>
                          <Button 
                            variant="outline" 
                            onClick={() => setBulkSettingsOpen(false)}
                          >
                            Отмена
                          </Button>
                        </div>
                      </div>
                    </DialogContent>
                  </Dialog>
                  
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={() => setSelectedProducts([])}
                    className="text-xs md:text-sm flex-1 sm:flex-none"
                  >
                    <span className="hidden sm:inline">Снять выбор</span>
                    <span className="sm:hidden">Снять</span>
                  </Button>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Список товаров */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>
              Товары ({filteredProducts.length})
            </CardTitle>
            {filteredProducts.length > 0 && (
              <div className="flex items-center gap-2">
                <Checkbox
                  checked={selectedProducts.length === filteredProducts.length}
                  onCheckedChange={handleSelectAll}
                />
                <span className="text-sm text-muted-foreground">
                  Выбрать все
                </span>
              </div>
            )}
          </div>
        </CardHeader>
        <CardContent className="p-3 md:p-6">
          {isLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-6 w-6 md:h-8 md:w-8 border-b-2 border-primary mx-auto mb-4"></div>
              <p className="text-xs md:text-sm">Загрузка товаров...</p>
            </div>
          ) : filteredProducts.length === 0 ? (
            <div className="text-center py-8">
              <Package className="h-8 w-8 md:h-12 md:w-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-base md:text-lg font-medium">Товары не найдены</p>
              <p className="text-sm md:text-base text-muted-foreground">Попробуйте изменить поисковый запрос</p>
            </div>
          ) : (
            <div className="space-y-2 md:space-y-3">
              {filteredProducts.map((product) => (
                <div key={product.id} className={`border rounded-lg p-3 md:p-4 transition-colors ${
                  selectedProducts.includes(product.id) ? 'bg-primary/5 border-primary/20' : ''
                }`}>
                  <div className="flex items-start gap-2 md:gap-4">
                    {/* Чекбокс и изображение */}
                    <div className="flex items-start gap-2 md:gap-3">
                      <Checkbox
                        checked={selectedProducts.includes(product.id)}
                        onCheckedChange={(checked) => handleSelectProduct(product.id, !!checked)}
                        className="mt-1"
                      />
                      <div className="w-12 h-12 md:w-16 md:h-16 rounded-lg overflow-hidden bg-muted">
                        <SafeImage 
                          src={product.image} 
                          alt={product.name}
                          className="w-full h-full"
                          fallbackText="Product"
                        />
                      </div>
                    </div>

                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="font-medium">{product.name}</h3>
                        <Badge variant="outline">{product.brand}</Badge>
                        <span className="text-sm text-muted-foreground">SKU: {product.article}</span>
                      </div>
                      
                      <div className="flex items-center gap-6 text-sm">
                        <div>
                          <span className="text-muted-foreground">Цена: </span>
                          <span className="font-medium">{formatPrice(product.price)}</span>
                        </div>
                        
                        {product.bot_enabled && (
                          <>
                            <div>
                              <span className="text-muted-foreground">Мин: </span>
                              <span className="text-green-600">{product.min_price ? formatPrice(product.min_price) : '—'}</span>
                            </div>
                            <div>
                              <span className="text-muted-foreground">Макс: </span>
                              <span className="text-red-600">{product.max_price ? formatPrice(product.max_price) : '—'}</span>
                            </div>
                            <div>
                              <span className="text-muted-foreground">Шаг: </span>
                              <span>{product.price_step ? formatPrice(product.price_step) : '—'}</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <TrendingUp className="h-4 w-4 text-muted-foreground" />
                              <span className="text-muted-foreground">Позиция: </span>
                              <span>{product.current_position || '—'}</span>
                              {product.target_position && (
                                <span className="text-blue-600">→ {product.target_position}</span>
                              )}
                            </div>
                          </>
                        )}
                      </div>
                    </div>

                    <div className="flex items-start pt-1">
                      <div className="flex items-center gap-2">
                        {product.bot_enabled ? (
                          <Power className="h-3 w-3 md:h-4 md:w-4 text-green-500" />
                        ) : (
                          <PowerOff className="h-3 w-3 md:h-4 md:w-4 text-red-500" />
                        )}
                        <Switch
                          checked={product.bot_enabled}
                          onCheckedChange={(checked) => toggleBot(product.id, checked)}
                          className="scale-75 md:scale-100"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default PriceBotSimple;
