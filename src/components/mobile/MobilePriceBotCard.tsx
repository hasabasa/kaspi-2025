// components/mobile/MobilePriceBotCard.tsx
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { 
  MoreVertical, 
  Power, 
  PowerOff, 
  Settings, 
  TrendingUp, 
  TrendingDown,
  DollarSign,
  Target
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator
} from "@/components/ui/dropdown-menu";
import { cn } from "@/lib/utils";
import { useMobileOptimizedSimple as useMobileOptimized } from "@/hooks/useMobileOptimizedSimple";
import { Product } from "@/services/kaspiStoreService";

interface MobilePriceBotCardProps {
  product: Product;
  isSelected?: boolean;
  onSelect?: (productId: string) => void;
  onToggleBot?: (productId: string, enabled: boolean) => void;
  onSettings?: (productId: string) => void;
  onQuickAction?: (productId: string, action: 'increase' | 'decrease') => void;
}

export const MobilePriceBotCard: React.FC<MobilePriceBotCardProps> = ({
  product,
  isSelected = false,
  onSelect,
  onToggleBot,
  onSettings,
  onQuickAction
}) => {
  const mobile = useMobileOptimized();
  const [isExpanded, setIsExpanded] = useState(false);

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('ru-KZ').format(price) + ' ₸';
  };

  const handleBotToggle = (enabled: boolean) => {
    onToggleBot?.(product.id, enabled);
  };

  const handleCardPress = () => {
    if (mobile.isSmallPhone) {
      setIsExpanded(!isExpanded);
    } else {
      onSelect?.(product.id);
    }
  };

  const getBotStatusColor = () => {
    if (!product.bot_enabled) return 'text-muted-foreground';
    return 'text-green-600 dark:text-green-400';
  };

  const getMarginInfo = () => {
    if (!product.min_margin || !product.max_margin) return null;
    return `${product.min_margin}-${product.max_margin}₸`;
  };

  return (
    <Card className={cn(
      "transition-all duration-200 active:scale-[0.98]",
      isSelected && "ring-2 ring-primary",
      product.bot_enabled && "border-green-200 dark:border-green-800",
      mobile.isSmallPhone && "shadow-sm"
    )}>
      {/* Main Card Content */}
      <CardContent className={mobile.isSmallPhone ? "p-3" : "p-4"}>
        <div 
          className="cursor-pointer"
          onClick={handleCardPress}
        >
          {/* Header */}
          <div className="flex items-start justify-between mb-3">
            <div className="flex items-start gap-3 flex-1 min-w-0">
              {/* Product Image */}
              {product.image && (
                <div className="flex-shrink-0">
                  <img 
                    src={product.image} 
                    alt={product.name}
                    className={cn(
                      "rounded-lg object-cover bg-muted",
                      mobile.isSmallPhone ? "w-12 h-12" : "w-16 h-16"
                    )}
                  />
                </div>
              )}

              {/* Product Info */}
              <div className="flex-1 min-w-0">
                <h3 className={cn(
                  "font-medium text-foreground line-clamp-2 leading-tight",
                  mobile.getTextSize('sm')
                )}>
                  {product.name}
                </h3>
                
                <div className={cn(
                  "flex items-center gap-2 mt-1",
                  mobile.getSpacing('xs')
                )}>
                  <Badge 
                    variant={product.bot_enabled ? "default" : "secondary"}
                    className={cn(
                      "text-xs",
                      mobile.isSmallPhone && "px-1 py-0.5"
                    )}
                  >
                    {product.bot_enabled ? 'Активен' : 'Выключен'}
                  </Badge>
                  
                  {product.bot_enabled && (
                    <div className={cn(
                      "flex items-center gap-1",
                      getBotStatusColor()
                    )}>
                      <Power className="h-3 w-3" />
                      <span className={mobile.getTextSize('xs')}>Работает</span>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-1 flex-shrink-0">
              <Switch
                checked={product.bot_enabled}
                onCheckedChange={handleBotToggle}
                size={mobile.isSmallPhone ? "sm" : "default"}
              />
              
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    className={cn(
                      mobile.touchTargetSize,
                      mobile.isSmallPhone && "h-8 w-8"
                    )}
                  >
                    <MoreVertical className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                
                <DropdownMenuContent align="end">
                  <DropdownMenuItem onClick={() => onSettings?.(product.id)}>
                    <Settings className="mr-2 h-4 w-4" />
                    Настройки
                  </DropdownMenuItem>
                  
                  <DropdownMenuSeparator />
                  
                  <DropdownMenuItem 
                    onClick={() => onQuickAction?.(product.id, 'increase')}
                  >
                    <TrendingUp className="mr-2 h-4 w-4" />
                    Повысить цену
                  </DropdownMenuItem>
                  
                  <DropdownMenuItem 
                    onClick={() => onQuickAction?.(product.id, 'decrease')}
                  >
                    <TrendingDown className="mr-2 h-4 w-4" />
                    Понизить цену
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>

          {/* Price and Margin Info */}
          <div className={cn(
            "grid gap-2",
            mobile.isSmallPhone ? "grid-cols-1" : "grid-cols-2"
          )}>
            <div className="bg-muted/50 rounded-lg p-2">
              <div className="flex items-center gap-1">
                <DollarSign className="h-3 w-3 text-muted-foreground" />
                <span className={cn(
                  "text-muted-foreground",
                  mobile.getTextSize('xs')
                )}>
                  Цена
                </span>
              </div>
              <div className={cn(
                "font-semibold text-foreground",
                mobile.getTextSize('sm')
              )}>
                {formatPrice(product.price)}
              </div>
            </div>

            {getMarginInfo() && (
              <div className="bg-muted/50 rounded-lg p-2">
                <div className="flex items-center gap-1">
                  <Target className="h-3 w-3 text-muted-foreground" />
                  <span className={cn(
                    "text-muted-foreground",
                    mobile.getTextSize('xs')
                  )}>
                    Маржа
                  </span>
                </div>
                <div className={cn(
                  "font-semibold text-foreground",
                  mobile.getTextSize('sm')
                )}>
                  {getMarginInfo()}
                </div>
              </div>
            )}
          </div>

          {/* Expanded Info (только для маленьких экранов) */}
          {mobile.isSmallPhone && isExpanded && (
            <div className="mt-3 pt-3 border-t border-border space-y-2">
              {product.price_step && (
                <div className="flex justify-between">
                  <span className={mobile.getTextSize('xs')}>Шаг изменения:</span>
                  <span className={cn(
                    "font-medium",
                    mobile.getTextSize('xs')
                  )}>
                    {formatPrice(product.price_step)}
                  </span>
                </div>
              )}
              
              <div className="flex justify-between">
                <span className={mobile.getTextSize('xs')}>SKU:</span>
                <span className={cn(
                  "font-mono text-muted-foreground",
                  mobile.getTextSize('xs')
                )}>
                  {product.kaspi_sku || product.id}
                </span>
              </div>

              {/* Quick Actions для маленьких экранов */}
              <div className={cn("flex gap-2 mt-3", mobile.getSpacing('xs'))}>
                <Button
                  variant="outline"
                  size="sm"
                  className="flex-1"
                  onClick={(e) => {
                    e.stopPropagation();
                    onQuickAction?.(product.id, 'decrease');
                  }}
                >
                  <TrendingDown className="h-3 w-3 mr-1" />
                  Снизить
                </Button>
                
                <Button
                  variant="outline"
                  size="sm"
                  className="flex-1"
                  onClick={(e) => {
                    e.stopPropagation();
                    onSettings?.(product.id);
                  }}
                >
                  <Settings className="h-3 w-3 mr-1" />
                  Настройки
                </Button>
                
                <Button
                  variant="outline"
                  size="sm"
                  className="flex-1"
                  onClick={(e) => {
                    e.stopPropagation();
                    onQuickAction?.(product.id, 'increase');
                  }}
                >
                  <TrendingUp className="h-3 w-3 mr-1" />
                  Повысить
                </Button>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};
