// components/layout/MobileSidebar.tsx
import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { cn } from "@/lib/utils";
import { 
  TrendingUp, 
  BarChart3, 
  Calculator, 
  ShoppingBag, 
  MessageSquare, 
  Zap, 
  X,
  Home,
  ChevronRight
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useMobileOptimizedSimple as useMobileOptimized } from "@/hooks/useMobileOptimizedSimple";

interface MobileSidebarProps {
  isOpen: boolean;
  setIsOpen: (isOpen: boolean) => void;
}

interface MenuItem {
  id: string;
  path: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  description?: string;
}

const menuItems: MenuItem[] = [
  {
    id: 'dashboard',
    path: '/dashboard',
    label: 'Главная',
    icon: Home,
    description: 'Обзор системы'
  },
  {
    id: 'price-bot',
    path: '/dashboard/price-bot',
    label: 'Бот демпинга',
    icon: TrendingUp,
    description: 'Автоматизация цен'
  },
  {
    id: 'sales',
    path: '/dashboard/sales',
    label: 'Мои продажи',
    icon: BarChart3,
    description: 'Аналитика продаж'
  },
  {
    id: 'unit-economics',
    path: '/dashboard/unit-economics',
    label: 'Юнит-экономика',
    icon: Calculator,
    description: 'Расчет прибыли'
  },
  {
    id: 'preorders',
    path: '/dashboard/preorders',
    label: 'Предзаказы',
    icon: ShoppingBag,
    description: 'Управление предзаказами'
  },
  {
    id: 'whatsapp',
    path: '/dashboard/whatsapp',
    label: 'WhatsApp',
    icon: MessageSquare,
    description: 'Уведомления и рассылки'
  },
  {
    id: 'integrations',
    path: '/dashboard/integrations',
    label: 'Интеграции',
    icon: Zap,
    description: 'Подключение магазинов'
  }
];

export const MobileSidebar: React.FC<MobileSidebarProps> = ({
  isOpen,
  setIsOpen
}) => {
  const location = useLocation();
  const mobile = useMobileOptimized();
  const [touchStartY, setTouchStartY] = useState<number | null>(null);

  // Закрытие при клике вне области
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const sidebar = document.getElementById('mobile-sidebar');
      const target = event.target as Node;
      
      if (isOpen && sidebar && !sidebar.contains(target)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      document.body.style.overflow = 'hidden'; // Предотвращаем скролл
    } else {
      document.body.style.overflow = '';
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.body.style.overflow = '';
    };
  }, [isOpen, setIsOpen]);

  // Закрытие свайпом вниз
  const handleTouchStart = (event: React.TouchEvent) => {
    setTouchStartY(event.touches[0].clientY);
  };

  const handleTouchMove = (event: React.TouchEvent) => {
    if (!touchStartY) return;

    const currentY = event.touches[0].clientY;
    const diffY = currentY - touchStartY;

    // Если свайп вниз больше 100px - закрываем
    if (diffY > 100) {
      setIsOpen(false);
      setTouchStartY(null);
    }
  };

  const handleTouchEnd = () => {
    setTouchStartY(null);
  };

  // Закрытие при переходе на другую страницу
  const handleLinkClick = () => {
    setIsOpen(false);
  };

  if (!mobile.isMobile) return null;

  return (
    <>
      {/* Overlay */}
      <div
        className={cn(
          "fixed inset-0 bg-black/50 z-40 transition-opacity duration-300",
          isOpen ? "opacity-100" : "opacity-0 pointer-events-none"
        )}
        onClick={() => setIsOpen(false)}
      />

      {/* Sidebar */}
      <div
        id="mobile-sidebar"
        className={cn(
          "fixed bottom-0 left-0 right-0 z-50 bg-background border-t border-border transition-transform duration-300 ease-out",
          "rounded-t-2xl shadow-2xl",
          isOpen ? "translate-y-0" : "translate-y-full"
        )}
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
      >
        {/* Drag Handle */}
        <div className="flex justify-center py-3">
          <div className="w-12 h-1 bg-muted-foreground/30 rounded-full" />
        </div>

        {/* Header */}
        <div className="flex items-center justify-between px-6 pb-4">
          <div>
            <h2 className={cn("font-bold text-foreground", mobile.getTextSize('lg'))}>
              Панель управления
            </h2>
            <p className={cn("text-muted-foreground", mobile.getTextSize('sm'))}>
              Выберите модуль
            </p>
          </div>
          
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setIsOpen(false)}
            className={mobile.touchTargetSize}
          >
            <X className="h-5 w-5" />
          </Button>
        </div>

        {/* Navigation Menu */}
        <div className="max-h-[60vh] overflow-y-auto pb-safe">
          <div className={cn("px-4 pb-6", mobile.getSpacing('sm'))}>
            {menuItems.map((item) => {
              const isActive = location.pathname === item.path;
              const IconComponent = item.icon;

              return (
                <Link
                  key={item.id}
                  to={item.path}
                  onClick={handleLinkClick}
                  className={cn(
                    "flex items-center justify-between p-4 rounded-xl transition-all duration-200",
                    mobile.touchTargetSize,
                    isActive
                      ? "bg-primary text-primary-foreground shadow-lg scale-[0.98]"
                      : "hover:bg-muted active:bg-muted/80 active:scale-[0.98]"
                  )}
                >
                  <div className="flex items-center gap-3">
                    <div className={cn(
                      "p-2 rounded-lg transition-colors",
                      isActive 
                        ? "bg-primary-foreground/20" 
                        : "bg-muted"
                    )}>
                      <IconComponent className={cn(
                        "h-5 w-5",
                        isActive ? "text-primary-foreground" : "text-foreground"
                      )} />
                    </div>
                    
                    <div>
                      <div className={cn(
                        "font-medium",
                        mobile.getTextSize('base'),
                        isActive ? "text-primary-foreground" : "text-foreground"
                      )}>
                        {item.label}
                      </div>
                      {item.description && (
                        <div className={cn(
                          mobile.getTextSize('xs'),
                          isActive 
                            ? "text-primary-foreground/70" 
                            : "text-muted-foreground"
                        )}>
                          {item.description}
                        </div>
                      )}
                    </div>
                  </div>

                  <ChevronRight className={cn(
                    "h-4 w-4 transition-transform",
                    isActive 
                      ? "text-primary-foreground rotate-90" 
                      : "text-muted-foreground"
                  )} />
                </Link>
              );
            })}
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-border bg-muted/30">
          <div className={cn(
            "text-center text-muted-foreground",
            mobile.getTextSize('xs')
          )}>
            Kaspi Panel • Управление магазином
          </div>
        </div>
      </div>
    </>
  );
};
