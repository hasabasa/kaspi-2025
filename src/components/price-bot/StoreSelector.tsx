
import { useState, useEffect } from "react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Store, Package } from "lucide-react";
import { KaspiStore } from "@/types";
import { supabase } from "@/integrations/supabase/client";
import { useAuth } from "@/components/integration/useAuth";
import { useStoreContext } from "@/contexts/StoreContext";
import { useRouteConfig } from "@/hooks/useRouteConfig";

interface StoreSelectorProps {
  selectedStoreId: string | null;
  onStoreChange: (storeId: string | null) => void;
}

const StoreSelector = ({
  selectedStoreId,
  onStoreChange
}: StoreSelectorProps) => {
  const {
    user
  } = useAuth();
  const isDemo = !user;
  const {
    stores: globalStores,
    loading: globalLoading,
    setSelectedStore: setGlobalStore
  } = useStoreContext();
  const { currentConfig } = useRouteConfig();
  const [stores, setStores] = useState<KaspiStore[]>([]);
  const [loading, setLoading] = useState(false);

  // Демонстрационные магазины
  const demoStores: KaspiStore[] = [{
    id: 'demo-1',
    merchant_id: 'demo-123',
    name: 'Демонстрационный магазин',
    user_id: 'demo',
    api_key: '****',
    products_count: 157,
    last_sync: new Date().toISOString(),
    is_active: true,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }, {
    id: 'demo-2',
    merchant_id: 'demo-456',
    name: 'Тестовый магазин',
    user_id: 'demo',
    api_key: '****',
    products_count: 86,
    last_sync: new Date(Date.now() - 86400000).toISOString(),
    is_active: true,
    created_at: new Date(Date.now() - 604800000).toISOString(),
    updated_at: new Date(Date.now() - 86400000).toISOString()
  }];

  // Use global stores if available
  useEffect(() => {
    if (globalStores.length > 0) {
      setStores(globalStores);
    } else if (isDemo) {
      setStores(demoStores);
    } else if (user) {
      loadStores();
    }
  }, [user, globalStores]);

  // Auto-select first store if no store is selected or "all" is not allowed
  useEffect(() => {
    if (stores.length > 0) {
      if (!selectedStoreId || (selectedStoreId === 'all' && !currentConfig.allowAllStores)) {
        const firstStore = stores[0];
        onStoreChange(firstStore.id);
      }
    }
  }, [stores, selectedStoreId, onStoreChange, currentConfig.allowAllStores]);

  const loadStores = async () => {
    if (!user) return;
    setLoading(true);
    try {
      const {
        data,
        error
      } = await supabase.from('kaspi_stores').select('*').eq('user_id', user.id).eq('is_active', true);
      if (error) throw error;
      setStores(data as KaspiStore[] || []);
    } catch (error: any) {
      console.error('Error loading stores:', error);
    } finally {
      setLoading(false);
    }
  };

  // Synchronize with global store context
  const handleStoreChange = (storeId: string | null) => {
    // Prevent selecting "all" if not allowed in current module
    if (storeId === 'all' && !currentConfig.allowAllStores) {
      return;
    }
    onStoreChange(storeId);
    // Also update global context
    setGlobalStore(storeId);
  };

  const selectedStore = stores.find(store => store.id === selectedStoreId);
  const totalProducts = selectedStore?.products_count || 0;
  const isLoading = loading || globalLoading;

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-base">
          <Store className="h-5 w-5" />
          Выбор магазина
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <Select
            value={selectedStoreId || ''}
            onValueChange={handleStoreChange}
            disabled={isLoading}
          >
            <SelectTrigger className="bg-white">
              <SelectValue placeholder="Выберите магазин" />
            </SelectTrigger>
            <SelectContent className="bg-white border border-gray-200 shadow-lg z-50">
              {currentConfig.allowAllStores && (
                <SelectItem value="all" className="cursor-pointer hover:bg-gray-50">
                  <div className="flex items-center gap-2">
                    <Store className="h-4 w-4 text-gray-500" />
                    <span>Все магазины</span>
                    <span className="text-xs text-gray-500 ml-auto">
                      ({stores.reduce((sum, store) => sum + (store.products_count || 0), 0)})
                    </span>
                  </div>
                </SelectItem>
              )}
              {stores.map((store) => (
                <SelectItem key={store.id} value={store.id} className="cursor-pointer hover:bg-gray-50">
                  <div className="flex items-center gap-2">
                    <Store className="h-4 w-4 text-primary" />
                    <span className="truncate">{store.name}</span>
                    <span className="text-xs text-gray-500 ml-auto">
                      ({store.products_count || 0})
                    </span>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          {selectedStore && (
            <div className="text-sm text-muted-foreground bg-primary/5 p-3 rounded-lg border border-primary/20">
              <div className="flex items-center gap-2">
                <Package className="h-4 w-4 text-primary" />
                <span>
                  <strong>{selectedStore.name}</strong> - {totalProducts} товаров
                </span>
              </div>
            </div>
          )}

          {stores.length === 0 && !isLoading && (
            <div className="text-center py-4 text-gray-500 text-sm">
              {isDemo ? 'Загрузка демонстрационных магазинов...' : 'Добавьте магазины через интеграцию с Kaspi'}
            </div>
          )}

          {isLoading && (
            <div className="text-center py-4">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary mx-auto"></div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default StoreSelector;
