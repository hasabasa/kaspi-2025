
import { useStoreContext } from "@/contexts/StoreContext";
import { useAuth } from "@/components/integration/useAuth";

export const useStoreConnection = () => {
  const { stores, loading, selectedStoreId } = useStoreContext();
  const { user } = useAuth();

  // Consider demo (no-auth) mode when there is no authenticated user
  const isDemo = !user;

  const hasStores = stores.length > 0;
  const isConnected = hasStores || isDemo;
  const needsConnection = !isConnected && !loading;

  return {
    hasStores,
    isConnected,
    needsConnection,
    loading,
    stores,
    selectedStoreId
  };
};
