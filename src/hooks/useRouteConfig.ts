
import { useLocation } from 'react-router-dom';
import { useModuleConfig } from '@/contexts/ModuleConfigContext';

export const useRouteConfig = () => {
  const location = useLocation();
  const { currentConfig, getConfigForRoute } = useModuleConfig();

  return {
    currentConfig,
    getConfigForRoute,
    currentRoute: location.pathname
  };
};
