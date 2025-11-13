// hooks/useDemperWebSocket.ts
import { useState, useEffect, useRef, useCallback } from 'react';
import { toast } from 'sonner';

interface DemperStatus {
  type: 'demper_status';
  store_id: string;
  status: 'active' | 'inactive' | 'error' | 'starting' | 'stopping';
  products_active: number;
  products_processed: number;
  last_update: string;
  uptime_seconds: number;
}

interface PriceUpdate {
  type: 'price_update';
  store_id: string;
  product_id: string;
  product_name: string;
  old_price: number;
  new_price: number;
  competitor_price: number;
  min_profit: number;
  timestamp: string;
  success: boolean;
}

interface DemperError {
  type: 'demper_error';
  store_id: string;
  error_message: string;
  product_id?: string;
  timestamp: string;
}

type WebSocketMessage = DemperStatus | PriceUpdate | DemperError | {
  type: 'connection_established' | 'pong' | 'error';
  [key: string]: any;
};

interface UseDemperWebSocketReturn {
  status: DemperStatus | null;
  recentUpdates: PriceUpdate[];
  errors: DemperError[];
  isConnected: boolean;
  connect: () => void;
  disconnect: () => void;
  sendMessage: (message: any) => void;
  clearUpdates: () => void;
  clearErrors: () => void;
}

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'ws://localhost:8010';

export function useDemperWebSocket(storeId: string | null): UseDemperWebSocketReturn {
  const [status, setStatus] = useState<DemperStatus | null>(null);
  const [recentUpdates, setRecentUpdates] = useState<PriceUpdate[]>([]);
  const [errors, setErrors] = useState<DemperError[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  
  const ws = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const pingIntervalRef = useRef<NodeJS.Timeout>();

  const connect = useCallback(() => {
    if (!storeId || ws.current?.readyState === WebSocket.OPEN) return;

    try {
      const wsUrl = BACKEND_URL.replace('http', 'ws') + `/ws/demper/${storeId}`;
      ws.current = new WebSocket(wsUrl);

      ws.current.onopen = () => {
        console.log('WebSocket connected for store:', storeId);
        setIsConnected(true);
        
        // Очищаем предыдущий таймаут переподключения
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
        }

        // Начинаем ping каждые 30 секунд
        pingIntervalRef.current = setInterval(() => {
          if (ws.current?.readyState === WebSocket.OPEN) {
            ws.current.send(JSON.stringify({ type: 'ping' }));
          }
        }, 30000);
      };

      ws.current.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          
          switch (message.type) {
            case 'demper_status':
              setStatus(message as DemperStatus);
              break;
              
            case 'price_update':
              const priceUpdate = message as PriceUpdate;
              setRecentUpdates(prev => {
                const newUpdates = [priceUpdate, ...prev].slice(0, 50); // Храним последние 50 обновлений
                return newUpdates;
              });
              
              // Показываем toast уведомление о изменении цены
              if (priceUpdate.success) {
                toast.success(
                  `Цена обновлена: ${priceUpdate.product_name}`,
                  {
                    description: `${priceUpdate.old_price}₸ → ${priceUpdate.new_price}₸`,
                    duration: 3000,
                  }
                );
              } else {
                toast.error(
                  `Ошибка обновления цены: ${priceUpdate.product_name}`,
                  { duration: 5000 }
                );
              }
              break;
              
            case 'demper_error':
              const error = message as DemperError;
              setErrors(prev => {
                const newErrors = [error, ...prev].slice(0, 20); // Храним последние 20 ошибок
                return newErrors;
              });
              
              // Показываем toast об ошибке только для критических ошибок
              if (!error.error_message.includes('Нет конкурентов')) {
                toast.error(
                  'Ошибка демпера',
                  {
                    description: error.error_message,
                    duration: 5000,
                  }
                );
              }
              break;
              
            case 'connection_established':
              console.log('WebSocket connection established');
              break;
              
            case 'pong':
              // Ответ на ping - просто подтверждаем что соединение живое
              break;
              
            default:
              console.log('Unknown WebSocket message:', message);
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.current.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        setIsConnected(false);
        
        // Очищаем ping интервал
        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current);
        }
        
        // Пытаемся переподключиться через 5 секунд
        if (event.code !== 1000) { // Не переподключаемся если закрытие было намеренным
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log('Attempting to reconnect WebSocket...');
            connect();
          }, 5000);
        }
      };

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setIsConnected(false);
      };

    } catch (error) {
      console.error('Error creating WebSocket connection:', error);
      setIsConnected(false);
    }
  }, [storeId]);

  const disconnect = useCallback(() => {
    if (ws.current) {
      ws.current.close(1000, 'Manual disconnect');
      ws.current = null;
    }
    
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    
    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
    }
    
    setIsConnected(false);
  }, []);

  const sendMessage = useCallback((message: any) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message));
    }
  }, []);

  const clearUpdates = useCallback(() => {
    setRecentUpdates([]);
  }, []);

  const clearErrors = useCallback(() => {
    setErrors([]);
  }, []);

  // Автоматическое подключение при изменении storeId
  useEffect(() => {
    if (storeId) {
      connect();
    } else {
      disconnect();
    }

    // Cleanup при размонтировании компонента
    return () => {
      disconnect();
    };
  }, [storeId, connect, disconnect]);

  // Cleanup таймеров при размонтировании
  useEffect(() => {
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (pingIntervalRef.current) {
        clearInterval(pingIntervalRef.current);
      }
    };
  }, []);

  return {
    status,
    recentUpdates,
    errors,
    isConnected,
    connect,
    disconnect,
    sendMessage,
    clearUpdates,
    clearErrors,
  };
}
