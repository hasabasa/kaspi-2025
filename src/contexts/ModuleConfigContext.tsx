
import React, { createContext, useContext, ReactNode } from 'react';
import { useLocation } from 'react-router-dom';

export interface ModuleConfig {
  showSelector: boolean;
  allowAllStores: boolean;
}

interface ModuleConfigContextType {
  currentConfig: ModuleConfig;
  getConfigForRoute: (route: string) => ModuleConfig;
}

const moduleConfigs: Record<string, ModuleConfig> = {
  '/dashboard/price-bot': { showSelector: true, allowAllStores: true },
  '/dashboard/sales': { showSelector: true, allowAllStores: false },
  '/dashboard/unit-economics': { showSelector: false, allowAllStores: false },
  '/dashboard/whatsapp': { showSelector: false, allowAllStores: false },
  '/dashboard/niche-search': { showSelector: false, allowAllStores: false },
  '/dashboard/preorders': { showSelector: true, allowAllStores: false },
  '/dashboard/tasks': { showSelector: false, allowAllStores: false },
  '/dashboard/subscription': { showSelector: false, allowAllStores: false },
  '/dashboard/integrations': { showSelector: false, allowAllStores: false }
};

const defaultConfig: ModuleConfig = { showSelector: true, allowAllStores: true };

const ModuleConfigContext = createContext<ModuleConfigContextType | undefined>(undefined);

interface ModuleConfigProviderProps {
  children: ReactNode;
}

export const ModuleConfigProvider = ({ children }: ModuleConfigProviderProps) => {
  const location = useLocation();

  const getConfigForRoute = (route: string): ModuleConfig => {
    return moduleConfigs[route] || defaultConfig;
  };

  const currentConfig = getConfigForRoute(location.pathname);

  const value: ModuleConfigContextType = {
    currentConfig,
    getConfigForRoute
  };

  return (
    <ModuleConfigContext.Provider value={value}>
      {children}
    </ModuleConfigContext.Provider>
  );
};

export const useModuleConfig = () => {
  const context = useContext(ModuleConfigContext);
  if (context === undefined) {
    throw new Error('useModuleConfig must be used within a ModuleConfigProvider');
  }
  return context;
};
