import React, { useState, useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import SimpleStoreConnection from '@/components/store/SimpleStoreConnection';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';

const SimpleConnectPage: React.FC = () => {
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Проверяем, есть ли уже подключенный магазин в сессии
    const storeSession = localStorage.getItem('kaspi_store_session');
    if (storeSession) {
      setIsConnected(true);
    }
  }, []);

  const handleStoreConnected = (storeData: any) => {
    console.log('Store connected:', storeData);
    setIsConnected(true);
  };

  const handleGoToDashboard = () => {
    // Перенаправляем на главную страницу дашборда
    window.location.href = '/dashboard';
  };

  const handleStartOver = () => {
    localStorage.removeItem('kaspi_store_session');
    setIsConnected(false);
  };

  // Если уже подключен, показываем страницу успеха
  if (isConnected) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-4">
        <div className="max-w-md w-full text-center space-y-6">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto">
            <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
              <span className="text-white text-lg">✓</span>
            </div>
          </div>
          
          <div>
            <h1 className="text-2xl font-bold text-foreground mb-2">
              Магазин успешно подключен!
            </h1>
            <p className="text-muted-foreground">
              Теперь вы можете использовать все функции панели управления
            </p>
          </div>

          <div className="space-y-3">
            <Button 
              className="w-full" 
              onClick={handleGoToDashboard}
              size="lg"
            >
              Перейти к панели управления
            </Button>
            
            <Button 
              variant="outline" 
              className="w-full" 
              onClick={handleStartOver}
              size="sm"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Подключить другой магазин
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="w-full max-w-lg">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-foreground mb-2">
            Mark Bot
          </h1>
          <p className="text-muted-foreground text-lg">
            Панель управления для продавцов Kaspi.kz
          </p>
        </div>
        
        <SimpleStoreConnection onConnected={handleStoreConnected} />
        
        <div className="text-center mt-6">
          <p className="text-sm text-muted-foreground">
            Уже есть аккаунт?{' '}
            <a href="/auth" className="text-primary hover:underline">
              Войти в систему
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default SimpleConnectPage;
