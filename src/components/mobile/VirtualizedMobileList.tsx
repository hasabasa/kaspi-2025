// components/mobile/VirtualizedMobileList.tsx
import React, { useState, useEffect, useRef, useCallback } from 'react';
import { FixedSizeList as List } from 'react-window';
import { cn } from "@/lib/utils";
import { useMobileOptimized } from "@/hooks/useMobileOptimized";
import { Loader2, AlertCircle } from "lucide-react";

interface VirtualizedMobileListProps<T> {
  items: T[];
  renderItem: (item: T, index: number) => React.ReactNode;
  itemHeight?: number;
  overscan?: number;
  className?: string;
  emptyMessage?: string;
  loadingMessage?: string;
  errorMessage?: string;
  isLoading?: boolean;
  hasError?: boolean;
  onItemClick?: (item: T, index: number) => void;
  onEndReached?: () => void;
  endReachedThreshold?: number;
  refreshing?: boolean;
  onRefresh?: () => void;
  pullToRefreshEnabled?: boolean;
}

interface ItemRendererProps {
  index: number;
  style: React.CSSProperties;
}

export function VirtualizedMobileList<T>({
  items,
  renderItem,
  itemHeight = 80,
  overscan = 5,
  className,
  emptyMessage = "Нет данных для отображения",
  loadingMessage = "Загрузка...",
  errorMessage = "Ошибка загрузки данных",
  isLoading = false,
  hasError = false,
  onItemClick,
  onEndReached,
  endReachedThreshold = 0.8,
  refreshing = false,
  onRefresh,
  pullToRefreshEnabled = false
}: VirtualizedMobileListProps<T>) {
  const mobile = useMobileOptimized();
  const listRef = useRef<List>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  
  const [pullDistance, setPullDistance] = useState(0);
  const [isPulling, setIsPulling] = useState(false);
  const [touchStartY, setTouchStartY] = useState(0);
  
  // Определяем высоту контейнера
  const [containerHeight, setContainerHeight] = useState(
    mobile.isMobile ? window.innerHeight - 200 : 400
  );
  
  useEffect(() => {
    const updateHeight = () => {
      if (containerRef.current) {
        const rect = containerRef.current.getBoundingClientRect();
        const availableHeight = window.innerHeight - rect.top - 60;
        setContainerHeight(Math.max(300, availableHeight));
      }
    };
    
    updateHeight();
    window.addEventListener('resize', updateHeight);
    return () => window.removeEventListener('resize', updateHeight);
  }, []);
  
  // Pull to refresh логика
  const handleTouchStart = useCallback((e: TouchEvent) => {
    if (!pullToRefreshEnabled || !mobile.isMobile) return;
    
    const touch = e.touches[0];
    setTouchStartY(touch.clientY);
    setIsPulling(false);
  }, [pullToRefreshEnabled, mobile.isMobile]);
  
  const handleTouchMove = useCallback((e: TouchEvent) => {
    if (!pullToRefreshEnabled || !mobile.isMobile || refreshing) return;
    
    const touch = e.touches[0];
    const deltaY = touch.clientY - touchStartY;
    
    // Проверяем, что список находится в верхней позиции
    const list = listRef.current;
    if (list && deltaY > 0) {
      const scrollTop = (list.state as any).scrollOffset || 0;
      
      if (scrollTop === 0) {
        e.preventDefault();
        const distance = Math.min(deltaY * 0.5, 100);
        setPullDistance(distance);
        setIsPulling(distance > 60);
      }
    }
  }, [pullToRefreshEnabled, mobile.isMobile, refreshing, touchStartY]);
  
  const handleTouchEnd = useCallback(() => {
    if (!pullToRefreshEnabled || !mobile.isMobile) return;
    
    if (isPulling && onRefresh) {
      onRefresh();
    }
    
    setPullDistance(0);
    setIsPulling(false);
  }, [pullToRefreshEnabled, mobile.isMobile, isPulling, onRefresh]);
  
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    
    container.addEventListener('touchstart', handleTouchStart, { passive: false });
    container.addEventListener('touchmove', handleTouchMove, { passive: false });
    container.addEventListener('touchend', handleTouchEnd);
    
    return () => {
      container.removeEventListener('touchstart', handleTouchStart);
      container.removeEventListener('touchmove', handleTouchMove);
      container.removeEventListener('touchend', handleTouchEnd);
    };
  }, [handleTouchStart, handleTouchMove, handleTouchEnd]);
  
  // Обработка скролла для загрузки новых данных
  const handleScroll = useCallback(({ scrollOffset, scrollUpdateWasRequested }: any) => {
    if (!onEndReached || scrollUpdateWasRequested) return;
    
    const totalHeight = items.length * itemHeight;
    const visibleHeight = containerHeight;
    const threshold = totalHeight * endReachedThreshold;
    
    if (scrollOffset + visibleHeight >= threshold) {
      onEndReached();
    }
  }, [items.length, itemHeight, containerHeight, endReachedThreshold, onEndReached]);
  
  // Рендер элемента списка
  const ItemRenderer = useCallback(({ index, style }: ItemRendererProps) => {
    const item = items[index];
    if (!item) return null;
    
    return (
      <div
        style={style}
        className={cn(
          "flex items-center px-4 border-b border-border/50",
          mobile.isMobile && "active:bg-muted/50 transition-colors",
          onItemClick && "cursor-pointer"
        )}
        onClick={() => onItemClick?.(item, index)}
      >
        {renderItem(item, index)}
      </div>
    );
  }, [items, renderItem, mobile.isMobile, onItemClick]);
  
  // Состояния загрузки и ошибок
  if (hasError) {
    return (
      <div className={cn("flex flex-col items-center justify-center py-12", className)}>
        <AlertCircle className="h-12 w-12 text-destructive mb-4" />
        <p className="text-destructive text-center">{errorMessage}</p>
        {onRefresh && (
          <button
            onClick={onRefresh}
            className="mt-4 px-4 py-2 bg-primary text-primary-foreground rounded-lg"
          >
            Попробовать снова
          </button>
        )}
      </div>
    );
  }
  
  if (isLoading && items.length === 0) {
    return (
      <div className={cn("flex flex-col items-center justify-center py-12", className)}>
        <Loader2 className="h-8 w-8 animate-spin text-primary mb-4" />
        <p className="text-muted-foreground">{loadingMessage}</p>
      </div>
    );
  }
  
  if (items.length === 0) {
    return (
      <div className={cn("flex flex-col items-center justify-center py-12", className)}>
        <div className="w-16 h-16 bg-muted rounded-full flex items-center justify-center mb-4">
          <AlertCircle className="h-8 w-8 text-muted-foreground" />
        </div>
        <p className="text-muted-foreground text-center">{emptyMessage}</p>
      </div>
    );
  }
  
  return (
    <div 
      ref={containerRef}
      className={cn("relative w-full", className)}
      style={{ height: containerHeight }}
    >
      {/* Pull to refresh индикатор */}
      {pullToRefreshEnabled && pullDistance > 0 && (
        <div 
          className="absolute top-0 left-0 right-0 flex items-center justify-center bg-background/95 backdrop-blur-sm z-10 transition-transform"
          style={{ 
            transform: `translateY(${pullDistance - 60}px)`,
            height: 60
          }}
        >
          <div className="flex items-center gap-2">
            {refreshing ? (
              <Loader2 className="h-5 w-5 animate-spin text-primary" />
            ) : (
              <div 
                className={cn(
                  "h-5 w-5 rounded-full border-2 border-primary/30 transition-colors",
                  isPulling && "border-primary"
                )}
              />
            )}
            <span className="text-sm text-muted-foreground">
              {refreshing ? "Обновление..." : isPulling ? "Отпустите для обновления" : "Потяните для обновления"}
            </span>
          </div>
        </div>
      )}
      
      {/* Виртуализированный список */}
      <List
        ref={listRef}
        height={containerHeight}
        itemCount={items.length}
        itemSize={itemHeight}
        overscanCount={overscan}
        onScroll={handleScroll}
        className="mobile-scroll"
      >
        {ItemRenderer}
      </List>
      
      {/* Индикатор загрузки внизу */}
      {isLoading && items.length > 0 && (
        <div className="absolute bottom-0 left-0 right-0 flex items-center justify-center py-4 bg-background/95 backdrop-blur-sm">
          <Loader2 className="h-5 w-5 animate-spin text-primary mr-2" />
          <span className="text-sm text-muted-foreground">Загрузка...</span>
        </div>
      )}
    </div>
  );
}
