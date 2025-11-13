// components/layout/MobileHeader.tsx
import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { cn } from "@/lib/utils";
import { 
  Menu, 
  Bell, 
  User, 
  Search,
  ArrowLeft,
  MoreVertical,
  Settings,
  LogOut
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuTrigger,
  DropdownMenuSeparator 
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { useMobileOptimizedSimple as useMobileOptimized } from "@/hooks/useMobileOptimizedSimple";
import { useAuth } from "@/components/integration/useAuth";
import { useProfile } from "@/hooks/useProfile";

interface MobileHeaderProps {
  toggleSidebar: () => void;
  showBackButton?: boolean;
  title?: string;
  subtitle?: string;
  actions?: React.ReactNode;
}

const getModuleName = (pathname: string): string => {
  const moduleNames: Record<string, string> = {
    '/dashboard': 'Главная',
    '/dashboard/price-bot': 'Бот демпинга',
    '/dashboard/sales': 'Мои продажи',
    '/dashboard/unit-economics': 'Юнит-экономика',
    '/dashboard/preorders': 'Предзаказы',
    '/dashboard/whatsapp': 'WhatsApp',
    '/dashboard/integrations': 'Интеграции',
    '/dashboard/profile': 'Профиль'
  };
  
  return moduleNames[pathname] || 'Панель управления';
};

const getModuleIcon = (pathname: string): string => {
  const icons: Record<string, string> = {
    '/dashboard': '🏠',
    '/dashboard/price-bot': '🤖',
    '/dashboard/sales': '📊',
    '/dashboard/unit-economics': '🧮',
    '/dashboard/preorders': '🛍️',
    '/dashboard/whatsapp': '💬',
    '/dashboard/integrations': '⚡'
  };
  
  return icons[pathname] || '📱';
};

export const MobileHeader: React.FC<MobileHeaderProps> = ({
  toggleSidebar,
  showBackButton = false,
  title,
  subtitle,
  actions
}) => {
  const location = useLocation();
  const navigate = useNavigate();
  const mobile = useMobileOptimized();
  const { user, signOut } = useAuth();
  const { profile } = useProfile();
  const [notificationCount] = useState(3); // Mock notifications

  const currentTitle = title || getModuleName(location.pathname);
  const currentIcon = getModuleIcon(location.pathname);

  const handleBack = () => {
    if (window.history.length > 1) {
      navigate(-1);
    } else {
      navigate('/dashboard');
    }
  };

  const handleSignOut = async () => {
    try {
      await signOut();
      navigate("/auth", { replace: true });
    } catch (error) {
      console.error('Error during sign out:', error);
      navigate("/auth", { replace: true });
    }
  };

  const getInitials = () => {
    const name = profile?.full_name || user?.email || 'User';
    return name
      .split(' ')
      .map(word => word.charAt(0))
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  // Определяем высоту хедера в зависимости от размера экрана
  const headerHeight = mobile.isSmallPhone ? 'h-14' : 'h-16';
  const safeArea = 'pt-safe-top'; // Учитываем safe area для notch

  return (
    <header className={cn(
      "sticky top-0 z-30 bg-background/95 backdrop-blur-sm border-b border-border",
      headerHeight,
      safeArea
    )}>
      <div className={cn(
        "flex items-center justify-between h-full",
        mobile.containerPadding.replace('p-', 'px-')
      )}>
        
        {/* Left Section */}
        <div className="flex items-center gap-3 flex-1 min-w-0">
          {showBackButton ? (
            <Button
              variant="ghost"
              size="icon"
              onClick={handleBack}
              className={cn(mobile.touchTargetSize, "flex-shrink-0")}
            >
              <ArrowLeft className="h-5 w-5" />
            </Button>
          ) : (
            <Button
              variant="ghost"
              size="icon"
              onClick={toggleSidebar}
              className={cn(mobile.touchTargetSize, "flex-shrink-0")}
            >
              <Menu className="h-5 w-5" />
            </Button>
          )}

          {/* Title Section */}
          <div className="flex items-center gap-2 min-w-0 flex-1">
            <span className="text-lg">{currentIcon}</span>
            <div className="min-w-0 flex-1">
              <h1 className={cn(
                "font-semibold text-foreground truncate",
                mobile.getTextSize('base')
              )}>
                {currentTitle}
              </h1>
              {subtitle && (
                <p className={cn(
                  "text-muted-foreground truncate",
                  mobile.getTextSize('xs')
                )}>
                  {subtitle}
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Right Section */}
        <div className="flex items-center gap-2 flex-shrink-0">
          {/* Custom Actions */}
          {actions}

          {/* Search Button (только на больших мобильных) */}
          {!mobile.isSmallPhone && (
            <Button
              variant="ghost"
              size="icon"
              className={mobile.touchTargetSize}
              onClick={() => {
                // TODO: Implement search
              }}
            >
              <Search className="h-5 w-5" />
            </Button>
          )}

          {/* Notifications */}
          <Button
            variant="ghost"
            size="icon"
            className={cn(mobile.touchTargetSize, "relative")}
            onClick={() => {
              // TODO: Show notifications
            }}
          >
            <Bell className="h-5 w-5" />
            {notificationCount > 0 && (
              <Badge
                variant="destructive"
                className="absolute -top-1 -right-1 h-5 w-5 rounded-full p-0 text-xs flex items-center justify-center"
              >
                {notificationCount > 9 ? '9+' : notificationCount}
              </Badge>
            )}
          </Button>

          {/* User Menu */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                className={cn(
                  "relative rounded-full",
                  mobile.touchTargetSize
                )}
              >
                <Avatar className="h-8 w-8">
                  <AvatarImage src={profile?.avatar_url} />
                  <AvatarFallback className={mobile.getTextSize('xs')}>
                    {getInitials()}
                  </AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            
            <DropdownMenuContent align="end" className="w-56">
              <div className="flex items-center gap-2 p-2">
                <Avatar className="h-10 w-10">
                  <AvatarImage src={profile?.avatar_url} />
                  <AvatarFallback>{getInitials()}</AvatarFallback>
                </Avatar>
                <div className="flex flex-col space-y-1">
                  <p className={cn("font-medium", mobile.getTextSize('sm'))}>
                    {profile?.full_name || 'Пользователь'}
                  </p>
                  <p className={cn("text-muted-foreground", mobile.getTextSize('xs'))}>
                    {user?.email}
                  </p>
                </div>
              </div>
              
              <DropdownMenuSeparator />
              
              <DropdownMenuItem 
                onClick={() => navigate('/dashboard/profile')}
                className={mobile.touchTargetSize}
              >
                <User className="mr-2 h-4 w-4" />
                <span>Профиль</span>
              </DropdownMenuItem>
              
              <DropdownMenuItem className={mobile.touchTargetSize}>
                <Settings className="mr-2 h-4 w-4" />
                <span>Настройки</span>
              </DropdownMenuItem>
              
              <DropdownMenuSeparator />
              
              <DropdownMenuItem 
                onClick={handleSignOut}
                className={cn("text-red-600", mobile.touchTargetSize)}
              >
                <LogOut className="mr-2 h-4 w-4" />
                <span>Выйти</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
};
