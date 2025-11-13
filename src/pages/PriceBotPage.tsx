
import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Info, Bot, TrendingUp, Settings, DollarSign } from "lucide-react";
import StoreSelector from "@/components/price-bot/StoreSelector";
import ProductList from "@/components/price-bot/ProductList";
import PriceBotSettings from "@/components/price-bot/PriceBotSettings";
import ActivationSection from "@/components/price-bot/ActivationSection";
import ProfitSection from "@/components/price-bot/ProfitSection";
import { useAuth } from "@/components/integration/useAuth";
import AuthComponent from "@/components/integration/AuthComponent";
import { useStoreConnection } from "@/hooks/useStoreConnection";
import ConnectStoreButton from "@/components/store/ConnectStoreButton";
import LoadingScreen from "@/components/ui/loading-screen";
import { supabase } from "@/integrations/supabase/client";
import { Product } from "@/types";
import { useMobileResponsive } from "@/hooks/use-mobile-responsive";
import { cn } from "@/lib/utils";

const PriceBotPage = () => {
  const { user, loading: authLoading } = useAuth();
  const { isConnected, needsConnection, loading: storeLoading } = useStoreConnection();
  const { isMobile, isIPhoneMini, getMobileSpacing, getTouchTargetSize } = useMobileResponsive();
  const [selectedStoreId, setSelectedStoreId] = useState<string | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [loadingProducts, setLoadingProducts] = useState(false);

  // Demo products for demonstration
  const demoProducts: Product[] = [
    {
      id: 'demo-1',
      name: 'iPhone 15 Pro Max 256GB',
      price: 650000,
      image: 'https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=400',
      botActive: true,
      minProfit: 50000,
      maxProfit: 100000,
      store_id: 'demo-1',
      kaspi_product_id: 'demo-product-1',
      category: 'Электроника',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    },
    {
      id: 'demo-2', 
      name: 'Samsung Galaxy S24 Ultra',
      price: 580000,
      image: 'https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=400',
      botActive: false,
      minProfit: 45000,
      maxProfit: 90000,
      store_id: 'demo-1',
      kaspi_product_id: 'demo-product-2',
      category: 'Электроника',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }
  ];

  // Load products when store is selected
  useEffect(() => {
    if (selectedStoreId && isConnected) {
      loadProducts();
    }
  }, [selectedStoreId, isConnected]);

  const loadProducts = async () => {
    // If no authenticated user, use demo products
    if (!user) {
      setProducts(demoProducts);
      return;
    }

    if (!selectedStoreId || selectedStoreId === 'all') return;

    setLoadingProducts(true);
    try {
      const { data, error } = await supabase
        .from('products')
        .select('*')
        .eq('store_id', selectedStoreId);
      
      if (error) throw error;
      setProducts(data || []);
    } catch (error) {
      console.error('Error loading products:', error);
      setProducts([]);
    } finally {
      setLoadingProducts(false);
    }
  };

  const handleProductSelect = (productId: string) => {
    const product = products.find(p => p.id === productId);
    setSelectedProduct(product || null);
  };

  const handleSettingsSave = (settings: any) => {
    console.log('Settings saved:', settings);
    // Here you would save the settings to the database
    
    // Update the product in state
    if (settings.productId) {
      setProducts(prevProducts => 
        prevProducts.map(product => 
          product.id === settings.productId 
            ? { ...product, botActive: settings.isActive, minProfit: settings.minProfit }
            : product
        )
      );
      
      // Update selected product if it's the same
      if (selectedProduct?.id === settings.productId) {
        setSelectedProduct(prev => prev ? { ...prev, botActive: settings.isActive, minProfit: settings.minProfit } : null);
      }
    }
  };

  // Show loading screen while authentication or stores are loading
  if (authLoading || storeLoading) {
    return <LoadingScreen text="Загрузка данных магазинов..." />;
  }

  // No auth gating — show demo products when not authenticated

  return (
    <div className={cn("space-y-4 md:space-y-6", getMobileSpacing())}>
      <div className={isMobile ? "text-center" : ""}>
        <h1 className="text-2xl md:text-3xl font-bold mb-2">Бот демпинга</h1>
        <p className="text-muted-foreground text-sm md:text-base">
          Автоматическое управление ценами для победы в конкурентной борьбе
        </p>
      </div>

  {!user && (
        <Alert className="bg-primary/5 border-primary/20">
          <Info className="h-4 w-4 text-primary flex-shrink-0" />
          <AlertDescription className="text-primary text-xs md:text-sm">
            Вы просматриваете демонстрационные данные. Подключите свой магазин Kaspi.kz для работы с реальными товарами.
          </AlertDescription>
        </Alert>
      )}

      <div className={cn("grid gap-4 md:gap-6", isMobile ? "grid-cols-1" : "grid-cols-1 lg:grid-cols-4")}>
        <div className={cn(isMobile ? "order-2" : "lg:col-span-1")}>
          <StoreSelector
            selectedStoreId={selectedStoreId}
            onStoreChange={setSelectedStoreId}
          />
        </div>
        
        <div className={cn("space-y-4 md:space-y-6", isMobile ? "order-1" : "lg:col-span-3")}>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bot className="h-5 w-5" />
                Товары с ботом демпинга
              </CardTitle>
              <CardDescription>
                Нажмите на товар для настройки бота демпинга
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loadingProducts ? (
                <LoadingScreen text="Загрузка товаров..." />
              ) : (
                <ProductList 
                  products={products}
                  activeProductId={selectedProduct?.id || null}
                  onProductSelect={handleProductSelect}
                  onSettingsSave={handleSettingsSave}
                />
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default PriceBotPage;
