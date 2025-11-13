import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { Link2, Package, Plus, RefreshCw, Store, Trash2, AlertTriangle, LogIn } from "lucide-react";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { useAuth } from "./useAuth";
import { supabase } from "@/integrations/supabase/client";
import { KaspiStore } from "@/types";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useIsMobile } from "@/hooks/use-mobile";
import { API_URL, API_BASE_PATH } from "@/config";

const API_BASE_URL = `${API_URL}${API_BASE_PATH}`;

const KaspiIntegration = () => {
  const { user, loading: authLoading } = useAuth();
  const isMobile = useIsMobile();
  const [stores, setStores] = useState<KaspiStore[]>([]);
  const [isAddingStore, setIsAddingStore] = useState(false);
  const [kaspiEmail, setKaspiEmail] = useState("");
  const [kaspiPassword, setKaspiPassword] = useState("");
  const [isSyncing, setIsSyncing] = useState<string | null>(null);
  const [isConnecting, setIsConnecting] = useState(false);
  const [loadingStores, setLoadingStores] = useState(false);
  // demo mode is inferred when there's no authenticated user

  // Демонстрационные магазины
  const demoStores: KaspiStore[] = [
    {
      id: '1',
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
      id: '2',
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

  const loadUserStores = async () => {
    if (!user) return;
    
    setLoadingStores(true);
    try {
      const response = await fetch(`${API_BASE_URL}/kaspi/stores?user_id=${user.id}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setStores(data.stores || []);
    } catch (error: any) {
      console.error('Error loading stores:', error);
      toast.error(error.message.includes('Failed to fetch') 
        ? 'Не удалось подключиться к серверу'
        : error.message || 'Ошибка при загрузке магазинов'
      );
    } finally {
      setLoadingStores(false);
    }
  };

  useEffect(() => {
    if (user) {
      loadUserStores();
    } else {
      // Не показываем демо-данные, показываем пустой список
      setStores([]);
    }
  }, [user]);

  const handleConnectStore = async () => {
    if (!user) {
      toast.error("Пожалуйста, войдите в аккаунт для подключения магазина");
      return;
    }

    if (!kaspiEmail || !kaspiPassword) {
      toast.error("Пожалуйста, заполните все поля");
      return;
    }

    setIsConnecting(true);
    try {
      const response = await fetch(`${API_BASE_URL}/kaspi/auth`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: user.id,
          email: kaspiEmail,
          password: kaspiPassword,
          auth_method: "playwright" // Используем правильный метод авторизации
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Ошибка подключения магазина');
      }

      const result = await response.json();
      
      // Обновляем список магазинов после успешного добавления
      await loadUserStores();
      
      setIsAddingStore(false);
      setKaspiEmail("");
      setKaspiPassword("");
      toast.success(result.message || "Магазин успешно подключен!");
    } catch (error: any) {
      console.error('Error connecting store:', error);
      toast.error(error.message || 'Ошибка при подключении магазина. Проверьте данные для входа.');
    } finally {
      setIsConnecting(false);
    }
  };

  const handleRemoveStore = async (storeId: string) => {
    if (!user) {
      toast.error("Эта функция доступна только после входа в аккаунт");
      return;
    }
    
    try {
      const response = await fetch(`${API_BASE_URL}/kaspi/stores/${storeId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Ошибка отключения магазина');
      }

      setStores(stores.filter(store => store.id !== storeId));
      toast.success("Магазин успешно отключен");
    } catch (error: any) {
      console.error('Error removing store:', error);
      toast.error(error.message || 'Ошибка при отключении магазина');
    }
  };

  const handleSync = async (storeId: string) => {
    if (!user) {
      toast.error("Для синхронизации требуется авторизация");
      return;
    }
    
    setIsSyncing(storeId);
    try {
      const response = await fetch(`${API_BASE_URL}/kaspi/stores/${storeId}/sync`, {
        method: 'POST',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Ошибка синхронизации');
      }

      const result = await response.json();
      
      setStores(stores.map(store => 
        store.id === storeId 
          ? { 
              ...store, 
              products_count: result.products_count || store.products_count,
              last_sync: new Date().toISOString() 
            }
          : store
      ));
      
      toast.success(result.message || "Товары успешно синхронизированы");
    } catch (error: any) {
      console.error('Error syncing store:', error);
      toast.error(error.message || 'Ошибка синхронизации магазина');
    } finally {
      setIsSyncing(null);
    }
  };

  const demoAddStore = () => {
    if (user) {
      setIsAddingStore(true);
      return;
    }
    
    toast.error("Для добавления магазина требуется авторизация");
  };

  if (authLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <TooltipProvider>
      <div className="space-y-4 sm:space-y-6">
        {!user && (
          <Alert className="bg-amber-50 border-amber-200">
            <AlertTriangle className="h-4 w-4 text-amber-500 flex-shrink-0" />
            <AlertDescription className="text-amber-700 text-sm">
              Вы просматриваете демонстрационные данные. Для подключения реальных магазинов требуется 
              <Button variant="link" asChild className="p-0 h-auto font-semibold">
                <a href="/"> войти в систему</a>
              </Button>
            </AlertDescription>
          </Alert>
        )}

        {loadingStores ? (
          <div className="flex items-center justify-center p-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        ) : (
          <>
            {stores.map(store => (
              <Card key={store.id}>
                <CardHeader className="pb-3 sm:pb-6">
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex items-center gap-2 min-w-0">
                      <Store className="h-4 w-4 sm:h-5 sm:w-5 text-orange-500 flex-shrink-0" />
                      <div className="min-w-0">
                        <CardTitle className="text-base sm:text-lg truncate">
                          {store.name || `Магазин Kaspi ${store.merchant_id.slice(-4)}`}
                        </CardTitle>
                        <CardDescription className="text-xs sm:text-sm truncate">
                          ID: {store.merchant_id}
                        </CardDescription>
                      </div>
                    </div>
                    <Badge 
                      variant={store.is_active ? "default" : "secondary"} 
                      className="flex-shrink-0"
                    >
                      {store.is_active ? "Активен" : "Неактивен"}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className={`grid ${isMobile ? 'grid-cols-1 gap-3' : 'grid-cols-2 gap-4'}`}>
                    <div className="p-3 sm:p-4 bg-gray-50 rounded-lg">
                      <div className="text-xs sm:text-sm font-medium text-gray-500">Товаров</div>
                      <div className="mt-1 font-medium text-sm sm:text-base">
                        {store.products_count.toLocaleString('ru-RU')}
                      </div>
                    </div>
                    <div className="p-3 sm:p-4 bg-gray-50 rounded-lg">
                      <div className="text-xs sm:text-sm font-medium text-gray-500">Последняя синхронизация</div>
                      <div className="mt-1 font-medium text-xs sm:text-sm">
                        {store.last_sync 
                          ? new Date(store.last_sync).toLocaleString('ru-RU', {
                              day: 'numeric',
                              month: 'long',
                              hour: '2-digit',
                              minute: '2-digit'
                            })
                          : 'Никогда'}
                      </div>
                    </div>
                  </div>
                </CardContent>
                <CardFooter className={`${isMobile ? 'flex-col gap-2' : 'flex-row justify-between'} pt-3 sm:pt-6`}>
                  {isMobile ? (
                    <>
                      <Button 
                        onClick={() => handleSync(store.id)}
                        disabled={isSyncing === store.id || !user}
                        className="w-full text-sm"
                        size="sm"
                      >
                        <RefreshCw className={`mr-2 h-4 w-4 ${isSyncing === store.id ? 'animate-spin' : ''}`} />
                        {isSyncing === store.id ? 'Синхронизация...' : 'Синхронизировать'}
                      </Button>
                      <Button 
                        variant="outline" 
                        onClick={() => handleRemoveStore(store.id)}
                        disabled={!user}
                        className="w-full text-sm"
                        size="sm"
                      >
                        <Trash2 className="h-4 w-4 mr-2" />
                        Отключить
                      </Button>
                    </>
                  ) : (
                    <>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <Button 
                            onClick={() => handleSync(store.id)}
                            disabled={isSyncing === store.id || !user}
                            className="flex-1 mr-2"
                          >
                            <RefreshCw className={`mr-2 h-4 w-4 ${isSyncing === store.id ? 'animate-spin' : ''}`} />
                            {isSyncing === store.id ? 'Синхронизация...' : 'Синхронизировать товары'}
                          </Button>
                        </TooltipTrigger>
                        <TooltipContent>
                          Импортировать товары из магазина Kaspi
                        </TooltipContent>
                      </Tooltip>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <Button 
                            variant="outline" 
                            onClick={() => handleRemoveStore(store.id)}
                            disabled={!user}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </TooltipTrigger>
                        <TooltipContent>
                          Отключить магазин
                        </TooltipContent>
                      </Tooltip>
                    </>
                  )}
                </CardFooter>
              </Card>
            ))}

            {!isAddingStore ? (
              <Button 
                className="w-full text-sm sm:text-base" 
                onClick={demoAddStore}
                size={isMobile ? "sm" : "default"}
              >
                {user ? (
                  <>
                    <Plus className="mr-2 h-4 w-4" />
                    Подключить магазин Kaspi
                  </>
                ) : (
                  <>
                    <LogIn className="mr-2 h-4 w-4" />
                    Войдите для добавления магазина
                  </>
                )}
              </Button>
            ) : (
              <Card>
                <CardHeader className="pb-3 sm:pb-6">
                  <CardTitle className="text-base sm:text-lg">Подключение магазина Kaspi</CardTitle>
                  <CardDescription className="text-xs sm:text-sm">
                    Введите данные от вашего аккаунта Kaspi для автоматического подключения магазина
                  </CardDescription>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="space-y-3 sm:space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="kaspi-email" className="text-sm">Email от Kaspi</Label>
                      <Input
                        id="kaspi-email"
                        type="email"
                        placeholder="Введите email от аккаунта Kaspi"
                        value={kaspiEmail}
                        onChange={(e) => setKaspiEmail(e.target.value)}
                        className="text-sm"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="kaspi-password" className="text-sm">Пароль от Kaspi</Label>
                      <Input
                        id="kaspi-password"
                        type="password"
                        placeholder="Введите пароль от аккаунта Kaspi"
                        value={kaspiPassword}
                        onChange={(e) => setKaspiPassword(e.target.value)}
                        className="text-sm"
                      />
                      <p className="text-xs text-gray-500">
                        Ваши данные защищены и используются только для подключения магазина
                      </p>
                    </div>
                  </div>
                </CardContent>
                <CardFooter className={`${isMobile ? 'flex-col gap-2' : 'flex-row justify-between'} pt-3 sm:pt-6`}>
                  {isMobile ? (
                    <>
                      <Button 
                        onClick={handleConnectStore}
                        disabled={!kaspiEmail || !kaspiPassword || isConnecting}
                        className="w-full text-sm"
                        size="sm"
                      >
                        <Link2 className="mr-2 h-4 w-4" />
                        {isConnecting ? 'Подключение...' : 'Подключить магазин'}
                      </Button>
                      <Button 
                        variant="outline" 
                        onClick={() => {
                          setIsAddingStore(false);
                          setKaspiEmail("");
                          setKaspiPassword("");
                        }}
                        disabled={isConnecting}
                        className="w-full text-sm"
                        size="sm"
                      >
                        Отмена
                      </Button>
                    </>
                  ) : (
                    <>
                      <Button 
                        variant="outline" 
                        onClick={() => {
                          setIsAddingStore(false);
                          setKaspiEmail("");
                          setKaspiPassword("");
                        }}
                        className="mr-2"
                        disabled={isConnecting}
                      >
                        Отмена
                      </Button>
                      <Button 
                        onClick={handleConnectStore}
                        disabled={!kaspiEmail || !kaspiPassword || isConnecting}
                      >
                        <Link2 className="mr-2 h-4 w-4" />
                        {isConnecting ? 'Подключение...' : 'Подключить магазин'}
                      </Button>
                    </>
                  )}
                </CardFooter>
              </Card>
            )}
          </>
        )}
      </div>
    </TooltipProvider>
  );
};

export default KaspiIntegration;
