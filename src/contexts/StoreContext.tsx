
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useSearchParams, useLocation } from 'react-router-dom';
import { KaspiStore } from '@/types';
import { supabase } from '@/integrations/supabase/client';
import { useAuth } from '@/components/integration/useAuth';
import { toast } from 'sonner';

interface StoreContextType {
  selectedStoreId: string | null;
  selectedStore: KaspiStore | null;
  stores: KaspiStore[];
  loading: boolean;
  error: string | null;
  setSelectedStore: (storeId: string | null) => void;
  refreshStores: () => Promise<void>;
}

const StoreContext = createContext<StoreContextType | undefined>(undefined);

interface StoreContextProviderProps {
  children: ReactNode;
}

export const StoreContextProvider = ({ children }: StoreContextProviderProps) => {
  const { user } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const location = useLocation();
  
  const [selectedStoreId, setSelectedStoreId] = useState<string | null>(null);
  const [stores, setStores] = useState<KaspiStore[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Demo stores
  const demoStores: KaspiStore[] = [
    {
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
    },
    {
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
    }
  ];

  // Module configurations
  const moduleConfigs: Record<string, { showSelector: boolean; allowAllStores: boolean }> = {
    '/dashboard/price-bot': { showSelector: true, allowAllStores: true },
    '/dashboard/sales': { showSelector: true, allowAllStores: false },
    '/dashboard/unit-economics': { showSelector: false, allowAllStores: false },
    '/dashboard/whatsapp': { showSelector: false, allowAllStores: false },
    '/dashboard/niche-search': { showSelector: false, allowAllStores: false },
    '/dashboard/preorders': { showSelector: true, allowAllStores: false },
    '/dashboard/crm': { showSelector: false, allowAllStores: false },
    '/dashboard/subscription': { showSelector: false, allowAllStores: false },
    '/dashboard/integrations': { showSelector: false, allowAllStores: false }
  };

  const getCurrentModuleConfig = () => {
    return moduleConfigs[location.pathname] || { showSelector: true, allowAllStores: true };
  };

  // Load stores function
  const loadStores = async () => {
    // Временно всегда показываем демо-магазины для демонстрации
    setStores(demoStores);
    return;

    setLoading(true);
    setError(null);
    
    try {
      const { data, error } = await supabase
        .from('kaspi_stores')
        .select('*')
        .eq('user_id', user.id)
        .eq('is_active', true);
      
      if (error) throw error;
      
      setStores(data as KaspiStore[] || []);
    } catch (error: any) {
      console.error('Error loading stores:', error);
      setError('Ошибка загрузки магазинов');
      toast.error('Ошибка загрузки магазинов');
    } finally {
      setLoading(false);
    }
  };

  // Set selected store with URL and localStorage persistence
  const setSelectedStore = (storeId: string | null) => {
    setSelectedStoreId(storeId);
    
    // Update URL params
    const newSearchParams = new URLSearchParams(searchParams);
    if (storeId && storeId !== 'all') {
      newSearchParams.set('storeId', storeId);
    } else {
      newSearchParams.delete('storeId');
    }
    setSearchParams(newSearchParams, { replace: true });
    
    // Save to localStorage
    if (storeId) {
      localStorage.setItem('selectedStoreId', storeId);
    } else {
      localStorage.removeItem('selectedStoreId');
    }
  };

  // Initialize from URL or localStorage, with module config consideration
  const initializeSelectedStore = () => {
    const moduleConfig = getCurrentModuleConfig();
    const urlStoreId = searchParams.get('storeId');
    const savedStoreId = localStorage.getItem('selectedStoreId');
    
    // If module doesn't allow "All stores" and current selection is "all", switch to first store
    if (!moduleConfig.allowAllStores && (selectedStoreId === 'all' || !selectedStoreId)) {
      if (stores.length > 0) {
        setSelectedStoreId(stores[0].id);
        return;
      }
    }
    
    // Check if URL store ID is valid
    if (urlStoreId && stores.find(store => store.id === urlStoreId)) {
      setSelectedStoreId(urlStoreId);
      return;
    }
    
    // Check if saved store ID is valid
    if (savedStoreId && savedStoreId !== 'null' && stores.find(store => store.id === savedStoreId)) {
      // If module doesn't allow "all" and saved is "all", switch to first store
      if (savedStoreId === 'all' && !moduleConfig.allowAllStores && stores.length > 0) {
        setSelectedStoreId(stores[0].id);
        return;
      }
      setSelectedStoreId(savedStoreId);
      return;
    }
    
    // Default behavior based on module config
    if (moduleConfig.allowAllStores) {
      setSelectedStoreId('all');
    } else if (stores.length > 0) {
      setSelectedStoreId(stores[0].id);
    }
  };

  // Load stores on user change
  useEffect(() => {
    loadStores();
  }, [user]);

  // Initialize selected store when stores change or route changes
  useEffect(() => {
    if (!loading) {
      initializeSelectedStore();
    }
  }, [stores, loading, location.pathname]);

  // Get selected store object
  const selectedStore = selectedStoreId && selectedStoreId !== 'all'
    ? stores.find(store => store.id === selectedStoreId) || null
    : null;

  const value: StoreContextType = {
    selectedStoreId,
    selectedStore,
    stores,
    loading,
    error,
    setSelectedStore,
    refreshStores: loadStores
  };

  return (
    <StoreContext.Provider value={value}>
      {children}
    </StoreContext.Provider>
  );
};

export const useStoreContext = () => {
  const context = useContext(StoreContext);
  if (context === undefined) {
    throw new Error('useStoreContext must be used within a StoreContextProvider');
  }
  return context;
};
