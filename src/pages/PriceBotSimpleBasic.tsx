// pages/PriceBotSimpleBasic.tsx
// Базовая версия без мобильной адаптации для тестирования

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Checkbox } from "@/components/ui/checkbox";
import { SafeImage } from "@/components/ui/SafeImage";
import { API_URL, API_BASE_PATH } from "@/config";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { ProductCard } from "@/components/price-bot/ProductCard";
import {
  Package,
  Search,
  Filter,
  Settings,
  Users,
  Power,
  PowerOff,
  Zap,
  Target,
  Image,
  TrendingUp
} from "lucide-react";
import { useStoreConnection } from "@/hooks/use-store-connection";
import { toast } from 'sonner';
import { useStoreContext } from "@/contexts/StoreContext";
import kaspiStoreService, { Product } from "@/services/kaspiStoreService";

const PriceBotSimpleBasic = () => {
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
  
  // Состояния
  const [products, setProducts] = useState<Product[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredProducts, setFilteredProducts] = useState<Product[]>([]);
  const [selectedProducts, setSelectedProducts] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [bulkSettingsOpen, setBulkSettingsOpen] = useState(false);
  const [bulkStrategy, setBulkStrategy] = useState<'aggressive' | 'balanced' | 'conservative'>('balanced');

  // Демо товары
  const demoProducts: Product[] = [
    {
      id: '1',
      name: 'iPhone 15 Pro Max 256GB',
      price: 650000,
      image: 'https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=400',
      bot_enabled: true,
      min_margin: 50000,
      max_margin: 100000,
      price_step: 5000,
      kaspi_sku: 'IPHONE-15-PRO-MAX-256',
      article: 'APPLE-001',
      brand: 'Apple',
      category: 'Электроника',
      current_position: 1,
      target_position: 1
    },
    {
      id: '2',
      name: 'Samsung Galaxy S24 Ultra',
      price: 580000,
      image: 'https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=400',
      bot_enabled: false,
      min_margin: 45000,
      max_margin: 90000,
      price_step: 4000,
      kaspi_sku: 'SAMSUNG-S24-ULTRA',
      article: 'SAMSUNG-001',
      brand: 'Samsung',
      category: 'Электроника',
      current_position: 3,
      target_position: 2
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
        name: product.name || '',
        price: product.price || 0,
        article: product.kaspi_sku || '',
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
    const filtered = products.filter(product =>
      product.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      product.article?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      product.brand?.toLowerCase().includes(searchQuery.toLowerCase())
    );
    setFilteredProducts(filtered);
  }, [products, searchQuery]);

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('ru-KZ').format(price) + ' ₸';
  };

  const activeBotsCount = products.filter(p => p.bot_enabled).length;

  const toggleBot = (productId: string, enabled: boolean) => {
    setProducts(prev => prev.map(p => 
      p.id === productId ? { ...p, bot_enabled: enabled } : p
    ));
    toast.success(enabled ? 'Бот включен' : 'Бот выключен');
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Заголовок */}
      <div>
        <h1 className="text-3xl font-bold mb-2">Прайс-бот</h1>
        <p className="text-muted-foreground">
          Простое управление ценами на ваши товары
        </p>
      </div>

      {/* Статистика */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <Package className="h-8 w-8 text-blue-500" />
              <div>
                <div className="text-2xl font-bold">{products.length}</div>
                <div className="text-sm text-muted-foreground">Всего товаров</div>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <Power className="h-8 w-8 text-green-500" />
              <div>
                <div className="text-2xl font-bold text-green-600">{activeBotsCount}</div>
                <div className="text-sm text-muted-foreground">Бот активен</div>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <PowerOff className="h-8 w-8 text-red-500" />
              <div>
                <div className="text-2xl font-bold text-red-600">{products.length - activeBotsCount}</div>
                <div className="text-sm text-muted-foreground">Бот неактивен</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Поиск и фильтры */}
      <Card>
        <CardHeader>
          <CardTitle>Поиск товаров</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Поиск по названию, артикулу или бренду..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Список товаров */}
      <Card>
        <CardHeader>
          <CardTitle>Товары ({filteredProducts.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
              <p>Загрузка товаров...</p>
            </div>
          ) : filteredProducts.length === 0 ? (
            <div className="text-center py-8">
              <Package className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-lg font-medium">Товары не найдены</p>
              <p className="text-muted-foreground">Попробуйте изменить поисковый запрос</p>
            </div>
          ) : (
            <div className="space-y-3">
              {filteredProducts.map((product) => (
                <div key={product.id} className="border rounded-lg p-4">
                  <div className="flex items-start gap-4">
                    {/* Изображение */}
                    <div className="w-16 h-16 rounded-lg overflow-hidden bg-muted">
                      <SafeImage 
                        src={product.image} 
                        alt={product.name}
                        className="w-full h-full"
                        fallbackText="Product"
                      />
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
                              <span className="text-muted-foreground">Мин маржа: </span>
                              <span className="text-green-600">{product.min_margin ? formatPrice(product.min_margin) : '—'}</span>
                            </div>
                            <div>
                              <span className="text-muted-foreground">Макс маржа: </span>
                              <span className="text-red-600">{product.max_margin ? formatPrice(product.max_margin) : '—'}</span>
                            </div>
                          </>
                        )}
                      </div>
                    </div>

                    <div className="flex items-start pt-1">
                      <div className="flex items-center gap-2">
                        {product.bot_enabled ? (
                          <Power className="h-4 w-4 text-green-500" />
                        ) : (
                          <PowerOff className="h-4 w-4 text-red-500" />
                        )}
                        <Switch
                          checked={product.bot_enabled}
                          onCheckedChange={(checked) => toggleBot(product.id, checked)}
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

export default PriceBotSimpleBasic;
