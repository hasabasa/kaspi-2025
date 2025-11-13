// components/demper/DemperActivityFeed.tsx
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { 
  TrendingDown, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle, 
  XCircle,
  Trash2,
  Clock
} from "lucide-react";
import { cn } from "@/lib/utils";

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

interface DemperActivityFeedProps {
  priceUpdates: PriceUpdate[];
  errors: DemperError[];
  onClearUpdates: () => void;
  onClearErrors: () => void;
  className?: string;
}

const formatTime = (timestamp: string): string => {
  try {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('ru', { 
      hour: '2-digit', 
      minute: '2-digit',
      second: '2-digit'
    });
  } catch {
    return 'Неизвестно';
  }
};

const formatPrice = (price: number): string => {
  return new Intl.NumberFormat('ru-KZ').format(price) + ' ₸';
};

const getPriceChangeIcon = (oldPrice: number, newPrice: number) => {
  if (newPrice < oldPrice) {
    return <TrendingDown className="h-4 w-4 text-green-500" />;
  } else if (newPrice > oldPrice) {
    return <TrendingUp className="h-4 w-4 text-red-500" />;
  }
  return <Clock className="h-4 w-4 text-gray-500" />;
};

const PriceUpdateItem: React.FC<{ update: PriceUpdate }> = ({ update }) => {
  const isDecrease = update.new_price < update.old_price;
  const priceChange = update.new_price - update.old_price;
  
  return (
    <div className="flex items-start gap-3 p-3 border rounded-lg">
      <div className="flex-shrink-0 mt-0.5">
        {update.success ? (
          <CheckCircle className="h-4 w-4 text-green-500" />
        ) : (
          <XCircle className="h-4 w-4 text-red-500" />
        )}
      </div>
      
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <p className="font-medium text-sm truncate">
            {update.product_name}
          </p>
          {getPriceChangeIcon(update.old_price, update.new_price)}
        </div>
        
        <div className="flex items-center gap-2 text-xs text-muted-foreground mb-2">
          <span>{formatTime(update.timestamp)}</span>
          <Badge 
            variant={update.success ? "default" : "destructive"}
            className="text-xs px-1 py-0"
          >
            {update.success ? 'Успешно' : 'Ошибка'}
          </Badge>
        </div>
        
        <div className="grid grid-cols-2 gap-2 text-xs">
          <div>
            <span className="text-muted-foreground">Цена: </span>
            <span className={cn(
              "font-medium",
              isDecrease ? "text-green-600" : "text-red-600"
            )}>
              {formatPrice(update.old_price)} → {formatPrice(update.new_price)}
            </span>
          </div>
          <div>
            <span className="text-muted-foreground">Конкурент: </span>
            <span className="font-medium">{formatPrice(update.competitor_price)}</span>
          </div>
        </div>
        
        {priceChange !== 0 && (
          <div className="mt-1 text-xs">
            <span className="text-muted-foreground">Изменение: </span>
            <span className={cn(
              "font-medium",
              isDecrease ? "text-green-600" : "text-red-600"
            )}>
              {priceChange > 0 ? '+' : ''}{formatPrice(Math.abs(priceChange))}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

const ErrorItem: React.FC<{ error: DemperError }> = ({ error }) => {
  const isNoCompetitors = error.error_message.includes('Нет конкурентов');
  
  return (
    <div className="flex items-start gap-3 p-3 border rounded-lg border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-950/20">
      <div className="flex-shrink-0 mt-0.5">
        <AlertTriangle className="h-4 w-4 text-red-500" />
      </div>
      
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <Badge 
            variant={isNoCompetitors ? "secondary" : "destructive"}
            className="text-xs"
          >
            {isNoCompetitors ? 'Предупреждение' : 'Ошибка'}
          </Badge>
          <span className="text-xs text-muted-foreground">
            {formatTime(error.timestamp)}
          </span>
        </div>
        
        <p className="text-sm text-red-600 dark:text-red-400 mb-1">
          {error.error_message}
        </p>
        
        {error.product_id && (
          <p className="text-xs text-muted-foreground">
            ID товара: {error.product_id}
          </p>
        )}
      </div>
    </div>
  );
};

export const DemperActivityFeed: React.FC<DemperActivityFeedProps> = ({
  priceUpdates,
  errors,
  onClearUpdates,
  onClearErrors,
  className
}) => {
  const hasUpdates = priceUpdates.length > 0;
  const hasErrors = errors.length > 0;
  
  // Объединяем и сортируем все активности по времени
  const allActivities = [
    ...priceUpdates.map(update => ({ ...update, activityType: 'update' as const })),
    ...errors.map(error => ({ ...error, activityType: 'error' as const }))
  ].sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());

  return (
    <Card className={cn("", className)}>
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">Активность демпера</CardTitle>
          <div className="flex items-center gap-2">
            {hasUpdates && (
              <Button 
                variant="outline" 
                size="sm" 
                onClick={onClearUpdates}
                className="text-xs"
              >
                <Trash2 className="h-3 w-3 mr-1" />
                Очистить обновления
              </Button>
            )}
            {hasErrors && (
              <Button 
                variant="outline" 
                size="sm" 
                onClick={onClearErrors}
                className="text-xs"
              >
                <Trash2 className="h-3 w-3 mr-1" />
                Очистить ошибки
              </Button>
            )}
          </div>
        </div>
        
        <div className="flex items-center gap-4 text-sm text-muted-foreground">
          <span>Обновлений: {priceUpdates.length}</span>
          <span>Ошибок: {errors.length}</span>
        </div>
      </CardHeader>
      
      <CardContent>
        {allActivities.length === 0 ? (
          <div className="text-center py-8">
            <Clock className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
            <p className="text-muted-foreground">Нет активности</p>
            <p className="text-xs text-muted-foreground mt-1">
              Изменения цен и ошибки будут отображаться здесь
            </p>
          </div>
        ) : (
          <ScrollArea className="h-[400px]">
            <div className="space-y-3">
              {allActivities.map((activity, index) => (
                <div key={`${activity.activityType}-${index}`}>
                  {activity.activityType === 'update' ? (
                    <PriceUpdateItem update={activity as PriceUpdate} />
                  ) : (
                    <ErrorItem error={activity as DemperError} />
                  )}
                </div>
              ))}
            </div>
          </ScrollArea>
        )}
      </CardContent>
    </Card>
  );
};
