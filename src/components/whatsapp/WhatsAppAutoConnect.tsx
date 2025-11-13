
import { useEffect, useState } from 'react';
import { useMobileOptimizedSimple as useMobileOptimized } from "@/hooks/useMobileOptimizedSimple";
import { cn } from "@/lib/utils";

export default function WhatsAppAutoConnect() {
  const mobile = useMobileOptimized();
  
  const [status, setStatus] = useState('⏳ Подключение к WhatsApp...');
  const [qrCode, setQrCode] = useState<string | null>(null);
  const [hasErrored, setHasErrored] = useState(false);

  const pollConnection = async () => {
    try {
      const res = await fetch('/qr');
      
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      
      const data = await res.json();

      if (data.qr) {
        setQrCode(data.qr);
        setStatus('📲 Пожалуйста, отсканируйте QR-код в WhatsApp');
      } else if (data.status === 'connected') {
        setQrCode(null);
        setStatus('✅ Ваш номер успешно подключен к авторассылке');
      } else {
        setStatus('⏳ Ожидание QR-кода...');
      }
    } catch (err) {
      if (!hasErrored) {
        console.log('WhatsApp: Бэкенд недоступен, показываем демо-режим');
        setHasErrored(true);
      }
      setStatus('🚧 Демо-режим WhatsApp бота');
      setQrCode(null);
    }
  };

  useEffect(() => {
    pollConnection();
    // Если произошла ошибка, не продолжаем опрос
    if (!hasErrored) {
      const interval = setInterval(() => {
        if (!hasErrored) {
          pollConnection();
        }
      }, 5000);
      return () => clearInterval(interval);
    }
  }, [hasErrored]);

  return (
    <div className={cn(
      "flex flex-col items-center justify-center space-y-6",
      mobile.isMobile ? "min-h-[400px]" : "min-h-[500px]"
    )}>
      <div className="text-center">
        <h1 className={cn(
          "font-bold mb-2",
          mobile.isMobile ? mobile.getTextSize('xl') : "text-3xl"
        )}>
          WhatsApp бот
        </h1>
        <p className={cn(
          "text-muted-foreground mb-8",
          mobile.getTextSize('sm')
        )}>
          Автоматическая отправка сообщений клиентам
        </p>
      </div>
      
      <div className={cn(
        "bg-card rounded-lg shadow-lg text-center w-full",
        mobile.isSmallPhone ? "p-4 max-w-sm" : "p-8 max-w-md"
      )}>
        <div className={cn(
          "mb-4",
          mobile.getTextSize('base')
        )}>
          {status}
        </div>
        
        {qrCode && (
          <div className="mt-6">
            <img
              src={qrCode}
              alt="QR-код WhatsApp"
              className="mx-auto border rounded-lg"
              style={{ 
                width: mobile.isSmallPhone ? '200px' : '250px', 
                height: mobile.isSmallPhone ? '200px' : '250px' 
              }}
            />
            <p className={cn(
              "text-muted-foreground mt-2",
              mobile.getTextSize('xs')
            )}>
              Откройте WhatsApp на телефоне → Настройки → Связанные устройства → Отсканировать QR-код
            </p>
          </div>
        )}
        
        {status.includes('Демо-режим') && (
          <div className="mt-6 p-4 bg-primary/5 rounded-lg border border-primary/20">
            <h3 className="font-semibold text-primary mb-2">Возможности WhatsApp бота:</h3>
            <ul className="text-sm text-primary/80 text-left space-y-1">
              <li>• Автоматические уведомления о заказах</li>
              <li>• Отправка трек-номеров</li>
              <li>• Уведомления об изменении статуса</li>
              <li>• Персонализированные сообщения</li>
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
