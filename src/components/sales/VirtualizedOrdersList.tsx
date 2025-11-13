// components/sales/VirtualizedOrdersList.tsx
import React, { useMemo } from 'react';
import { FixedSizeList as List } from 'react-window';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { 
  Calendar, 
  Package, 
  TrendingUp, 
  Search,
  Download,
  RefreshCw,
  MoreHorizontal
} from "lucide-react";
import { cn } from "@/lib/utils";
import type { SalesOrder } from '@/services/salesService';

interface VirtualizedOrdersListProps {
  orders: SalesOrder[];
  searchQuery: string;
  onSearchChange: (query: string) => void;
  onLoadMore?: () => void;
  onRefresh?: () => void;
  onExport?: () => void;
  className?: string;
}

interface OrderItemProps {
  index: number;
  style: React.CSSProperties;
  data: SalesOrder[];
}

const OrderItem: React.FC<OrderItemProps> = ({ index, style, data }) => {
  const order = data[index];
  
  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      });
    } catch {
      return dateString;
    }
  };

  const formatTime = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleTimeString('ru-RU', {
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return '';
    }
  };

  const formatPrice = (amount: number) => {
    return new Intl.NumberFormat('ru-KZ').format(amount) + ' ₸';
  };

  return (
    <div style={style} className="px-4">
      <div className="border rounded-lg p-4 bg-card hover:bg-accent/50 transition-colors">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Calendar className="h-4 w-4 text-muted-foreground" />
            <div>
              <p className="font-medium">{formatDate(order.date)}</p>
              <p className="text-sm text-muted-foreground">{formatTime(order.date)}</p>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="text-right">
              <div className="flex items-center gap-2">
                <Package className="h-4 w-4 text-blue-500" />
                <span className="font-medium">{order.count} заказов</span>
              </div>
            </div>
            
            <div className="text-right">
              <div className="flex items-center gap-2">
                <TrendingUp className="h-4 w-4 text-green-500" />
                <span className="font-medium text-green-600">
                  {formatPrice(order.amount)}
                </span>
              </div>
              <p className="text-xs text-muted-foreground">
                ~{formatPrice(order.amount / order.count)} за заказ
              </p>
            </div>

            <Button variant="ghost" size="sm">
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export const VirtualizedOrdersList: React.FC<VirtualizedOrdersListProps> = ({
  orders,
  searchQuery,
  onSearchChange,
  onLoadMore,
  onRefresh,
  onExport,
  className
}) => {
  // Статистика
  const stats = useMemo(() => {
    const totalOrders = orders.reduce((sum, order) => sum + order.count, 0);
    const totalRevenue = orders.reduce((sum, order) => sum + order.amount, 0);
    const avgOrderValue = totalOrders > 0 ? totalRevenue / totalOrders : 0;
    
    return {
      totalOrders,
      totalRevenue,
      avgOrderValue,
      daysWithOrders: orders.length
    };
  }, [orders]);

  const formatPrice = (amount: number) => {
    return new Intl.NumberFormat('ru-KZ').format(amount) + ' ₸';
  };

  return (
    <Card className={cn("", className)}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Заказы ({orders.length} дней)</CardTitle>
          <div className="flex items-center gap-2">
            {onRefresh && (
              <Button 
                variant="outline" 
                size="sm" 
                onClick={onRefresh}
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Обновить
              </Button>
            )}
            {onExport && (
              <Button variant="outline" size="sm" onClick={onExport}>
                <Download className="h-4 w-4 mr-2" />
                Экспорт
              </Button>
            )}
          </div>
        </div>

        {/* Статистика */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
          <div className="text-center p-3 border rounded-lg">
            <div className="text-2xl font-bold text-blue-600">
              {stats.totalOrders}
            </div>
            <div className="text-sm text-muted-foreground">Всего заказов</div>
          </div>
          
          <div className="text-center p-3 border rounded-lg">
            <div className="text-2xl font-bold text-green-600">
              {formatPrice(stats.totalRevenue)}
            </div>
            <div className="text-sm text-muted-foreground">Общая выручка</div>
          </div>
          
          <div className="text-center p-3 border rounded-lg">
            <div className="text-2xl font-bold text-purple-600">
              {formatPrice(stats.avgOrderValue)}
            </div>
            <div className="text-sm text-muted-foreground">Средний чек</div>
          </div>
          
          <div className="text-center p-3 border rounded-lg">
            <div className="text-2xl font-bold text-orange-600">
              {stats.daysWithOrders}
            </div>
            <div className="text-sm text-muted-foreground">Дней с продажами</div>
          </div>
        </div>

        {/* Поиск */}
        <div className="flex items-center gap-2 mt-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Поиск по дате или сумме..."
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
              className="pl-10"
            />
          </div>
          {onLoadMore && (
            <Button variant="outline" onClick={onLoadMore}>
              Загрузить еще
            </Button>
          )}
        </div>
      </CardHeader>

      <CardContent>
        {orders.length === 0 ? (
          <div className="text-center py-8">
            <Package className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <p className="text-muted-foreground">Нет данных о заказах</p>
          </div>
        ) : (
          <div className="h-[600px] w-full">
            <List
              width={1000}
              height={600}
              itemCount={orders.length}
              itemSize={100}
              itemData={orders}
              className="custom-scrollbar"
              children={OrderItem}
            />
          </div>
        )}
      </CardContent>
    </Card>
  );
};
