// components/demper/DemperStatusIndicator.tsx
import React from 'react';
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { 
  Activity, 
  Square, 
  AlertTriangle, 
  RotateCcw, 
  Play, 
  Pause,
  Wifi,
  WifiOff
} from "lucide-react";
import { cn } from "@/lib/utils";

interface DemperStatus {
  type: 'demper_status';
  store_id: string;
  status: 'active' | 'inactive' | 'error' | 'starting' | 'stopping';
  products_active: number;
  products_processed: number;
  last_update: string;
  uptime_seconds: number;
}

interface DemperStatusIndicatorProps {
  status: DemperStatus | null;
  isConnected: boolean;
  onStart?: () => void;
  onStop?: () => void;
  onReconnect?: () => void;
  className?: string;
}

const getStatusConfig = (status: DemperStatus['status']) => {
  switch (status) {
    case 'active':
      return {
        label: 'Активен',
        color: 'bg-green-500',
        textColor: 'text-green-600 dark:text-green-400',
        icon: Activity,
        variant: 'default' as const
      };
    case 'inactive':
      return {
        label: 'Неактивен',
        color: 'bg-gray-500',
        textColor: 'text-gray-600 dark:text-gray-400',
        icon: Square,
        variant: 'secondary' as const
      };
    case 'error':
      return {
        label: 'Ошибка',
        color: 'bg-red-500',
        textColor: 'text-red-600 dark:text-red-400',
        icon: AlertTriangle,
        variant: 'destructive' as const
      };
    case 'starting':
      return {
        label: 'Запуск...',
        color: 'bg-blue-500',
        textColor: 'text-blue-600 dark:text-blue-400',
        icon: RotateCcw,
        variant: 'default' as const
      };
    case 'stopping':
      return {
        label: 'Остановка...',
        color: 'bg-orange-500',
        textColor: 'text-orange-600 dark:text-orange-400',
        icon: RotateCcw,
        variant: 'secondary' as const
      };
    default:
      return {
        label: 'Неизвестно',
        color: 'bg-gray-500',
        textColor: 'text-gray-600 dark:text-gray-400',
        icon: Square,
        variant: 'secondary' as const
      };
  }
};

const formatUptime = (seconds: number): string => {
  if (seconds < 60) return `${seconds}с`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}м`;
  return `${Math.floor(seconds / 3600)}ч ${Math.floor((seconds % 3600) / 60)}м`;
};

const formatLastUpdate = (timestamp: string): string => {
  try {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffSec = Math.floor(diffMs / 1000);
    
    if (diffSec < 60) return `${diffSec}с назад`;
    if (diffSec < 3600) return `${Math.floor(diffSec / 60)}м назад`;
    return date.toLocaleTimeString('ru');
  } catch {
    return 'Неизвестно';
  }
};

export const DemperStatusIndicator: React.FC<DemperStatusIndicatorProps> = ({
  status,
  isConnected,
  onStart,
  onStop,
  onReconnect,
  className
}) => {
  const statusConfig = status ? getStatusConfig(status.status) : null;
  const StatusIcon = statusConfig?.icon || Square;

  return (
    <Card className={cn("p-4", className)}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          {/* Индикатор подключения */}
          <div className="flex items-center gap-2">
            {isConnected ? (
              <Wifi className="h-4 w-4 text-green-500" />
            ) : (
              <WifiOff className="h-4 w-4 text-red-500" />
            )}
          </div>

          {/* Статус демпера */}
          {status && statusConfig ? (
            <div className="flex items-center gap-2">
              <div className="relative">
                <div className={cn(
                  "h-3 w-3 rounded-full",
                  statusConfig.color,
                  status.status === 'active' && "animate-pulse"
                )} />
              </div>
              <StatusIcon className={cn("h-4 w-4", statusConfig.textColor)} />
              <Badge variant={statusConfig.variant} className="font-medium">
                {statusConfig.label}
              </Badge>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <div className="h-3 w-3 rounded-full bg-gray-400" />
              <Square className="h-4 w-4 text-gray-400" />
              <Badge variant="secondary">
                {isConnected ? 'Загрузка...' : 'Не подключен'}
              </Badge>
            </div>
          )}
        </div>

        {/* Кнопки управления */}
        <div className="flex items-center gap-2">
          {!isConnected && (
            <Button 
              variant="outline" 
              size="sm" 
              onClick={onReconnect}
              className="text-xs"
            >
              <RotateCcw className="h-3 w-3 mr-1" />
              Переподключить
            </Button>
          )}
          
          {status && (
            <>
              {status.status === 'active' && (
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={onStop}
                  className="text-xs"
                >
                  <Pause className="h-3 w-3 mr-1" />
                  Остановить
                </Button>
              )}
              
              {(status.status === 'inactive' || status.status === 'error') && (
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={onStart}
                  className="text-xs"
                >
                  <Play className="h-3 w-3 mr-1" />
                  Запустить
                </Button>
              )}
            </>
          )}
        </div>
      </div>

      {/* Детальная информация */}
      {status && (
        <div className="mt-3 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <p className="text-muted-foreground">Активных товаров</p>
            <p className="font-medium">{status.products_active}</p>
          </div>
          <div>
            <p className="text-muted-foreground">Обработано</p>
            <p className="font-medium">{status.products_processed}</p>
          </div>
          <div>
            <p className="text-muted-foreground">Время работы</p>
            <p className="font-medium">{formatUptime(status.uptime_seconds)}</p>
          </div>
          <div>
            <p className="text-muted-foreground">Последнее обновление</p>
            <p className="font-medium">{formatLastUpdate(status.last_update)}</p>
          </div>
        </div>
      )}

      {/* Статус подключения */}
      <div className="mt-2 text-xs text-muted-foreground">
        WebSocket: {isConnected ? (
          <span className="text-green-600 dark:text-green-400">Подключен</span>
        ) : (
          <span className="text-red-600 dark:text-red-400">Не подключен</span>
        )}
      </div>
    </Card>
  );
};
