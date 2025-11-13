import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { AlertCircle, Store, Lock, Mail } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { toast } from 'sonner';
import kaspiStoreService from '@/services/kaspiStoreService';

interface SimpleStoreConnectionProps {
  onConnected?: (storeData: any) => void;
}

const SimpleStoreConnection: React.FC<SimpleStoreConnectionProps> = ({ onConnected }) => {
  const [kaspiEmail, setKaspiEmail] = useState('');
  const [kaspiPassword, setKaspiPassword] = useState('');
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState('');

  const handleConnect = async () => {
    if (!kaspiEmail || !kaspiPassword) {
      setError('Пожалуйста, заполните все поля');
      return;
    }

    setIsConnecting(true);
    setError('');

    try {
      // Создаем уникальный ID для сессии (вместо user_id)
      const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      
      const result = await kaspiStoreService.connectStoreSimple({
        session_id: sessionId,
        email: kaspiEmail,
        password: kaspiPassword,
      });
      
      // Сохраняем данные магазина в localStorage для текущей сессии
      const storeData = {
        id: result.id || sessionId,
        name: result.name || 'Мой магазин Kaspi',
        merchant_id: result.merchant_id || sessionId,
        email: kaspiEmail,
        is_active: true,
        session_id: sessionId,
        last_sync: result.last_sync || new Date().toISOString(),
        created_at: result.created_at || new Date().toISOString(),
        updated_at: result.updated_at || new Date().toISOString(),
        products_count: result.products_count || 0,
        total_sales: result.total_sales || 0,
        commission_percent: result.commission_percent || 12
      };

      localStorage.setItem('kaspi_store_session', JSON.stringify(storeData));
      
      toast.success("Магазин успешно подключен!");
      
      if (onConnected) {
        onConnected(storeData);
      }
      
    } catch (error: any) {
      console.error('Error connecting store:', error);
      const errorMessage = error.message || 'Ошибка при подключении магазина. Проверьте данные для входа.';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setIsConnecting(false);
    }
  };

  return (
    <div className="max-w-md mx-auto">
      <Card>
        <CardHeader className="text-center">
          <div className="mx-auto w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
            <Store className="h-6 w-6 text-primary" />
          </div>
          <CardTitle>Подключение магазина</CardTitle>
          <CardDescription>
            Введите данные для входа в ваш личный кабинет Kaspi.kz
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <div className="space-y-2">
            <Label htmlFor="kaspi-email">Email от Kaspi.kz</Label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
              <Input
                id="kaspi-email"
                type="email"
                placeholder="your-email@example.com"
                value={kaspiEmail}
                onChange={(e) => setKaspiEmail(e.target.value)}
                className="pl-10"
                disabled={isConnecting}
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="kaspi-password">Пароль</Label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
              <Input
                id="kaspi-password"
                type="password"
                placeholder="Введите пароль"
                value={kaspiPassword}
                onChange={(e) => setKaspiPassword(e.target.value)}
                className="pl-10"
                disabled={isConnecting}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    handleConnect();
                  }
                }}
              />
            </div>
          </div>

          <Button 
            className="w-full" 
            onClick={handleConnect} 
            disabled={isConnecting || !kaspiEmail || !kaspiPassword}
          >
            {isConnecting ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Подключение...
              </>
            ) : (
              'Подключить магазин'
            )}
          </Button>

          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertDescription className="text-sm">
              Ваши данные передаются в зашифрованном виде и используются только для подключения к API Kaspi.kz
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    </div>
  );
};

export default SimpleStoreConnection;
