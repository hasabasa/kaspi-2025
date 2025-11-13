import { LogIn, LogOut, User, Settings, HelpCircle, Bell, BarChart2, Menu } from "lucide-react";
import { MenuToggle } from "./Sidebar";
import ThemeToggle from "@/components/ui/theme-toggle";
import { Button } from "@/components/ui/button";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "@/components/integration/useAuth";
import { Badge } from "@/components/ui/badge";
import { useScreenSize } from "@/hooks/use-screen-size";
import { cn } from "@/lib/utils";
import { useState } from "react";
import { 
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import GlobalStoreSelector from "./GlobalStoreSelector";
import UserProfileModal from "@/components/profile/UserProfileModal";
import { useProfile } from "@/hooks/useProfile";

interface HeaderProps {
  toggleSidebar: () => void;
  isMobile?: boolean;
  sidebarOpen?: boolean;
}

const getModuleName = (pathname: string): string => {
  const moduleNames: Record<string, string> = {
    '/dashboard/price-bot': 'Бот демпинга',
    '/dashboard/sales': 'Анализ продаж',
    '/dashboard/unit-economics': 'Юнит-экономика',
    '/dashboard/preorders': 'Предзаказы',
    '/dashboard/whatsapp': 'WhatsApp рассылка',
    '/dashboard/integrations': 'Подключение магазина',
    '/dashboard/profile': 'Профиль',
    '/dashboard': 'Панель управления'
  };
  
  return moduleNames[pathname] || 'Панель управления';
};

const Header = ({
  toggleSidebar,
  isMobile = false,
  sidebarOpen = true
}: HeaderProps) => {
  const { user, signOut, loading } = useAuth();
  const { profile } = useProfile();
  const { isLargeDesktop, isExtraLargeDesktop } = useScreenSize();
  const location = useLocation();
  const navigate = useNavigate();
  const [isProfileModalOpen, setIsProfileModalOpen] = useState(false);

  const handleSignOut = async () => {
    try {
      console.log('Header: Starting sign out process');
      await signOut();
      console.log('Header: Navigating to auth page');
      navigate("/auth", { replace: true });
    } catch (error) {
      console.error('Header: Error during sign out:', error);
      navigate("/auth", { replace: true });
    }
  };

  const handleHelpClick = () => {
    const whatsappNumber = "+77474576759";
    const whatsappUrl = `https://wa.me/${whatsappNumber.replace('+', '')}`;
    window.open(whatsappUrl, '_blank');
  };

  const headerHeight = isExtraLargeDesktop ? "h-24" : isLargeDesktop ? "h-20" : "h-16";
  const headerPadding = isExtraLargeDesktop ? "px-8" : isLargeDesktop ? "px-6" : "px-4";
  const currentModuleName = getModuleName(location.pathname);

  const getInitials = () => {
    const name = profile?.full_name || user?.email || '';
    return name
      .split(' ')
      .map(word => word.charAt(0))
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const handleProfileClick = () => {
    setIsProfileModalOpen(true);
  };

  return (
    <>
      <header className={cn(
        "bg-background/95 backdrop-blur-sm shadow-sm border-b border-border flex justify-between items-center",
        headerHeight,
        headerPadding,
        "py-3 md:py-4"
      )}>
        <div className="flex items-center gap-3">
          {/* Кнопка переключения сайдбара для всех экранов */}
          <Button 
            variant="ghost" 
            size="icon"
            onClick={toggleSidebar}
            className="hover:bg-sidebar-accent text-sidebar-foreground hover:text-blue-600"
          >
            <Menu className="h-5 w-5" />
          </Button>
          
          {/* Show title only on larger screens when sidebar is collapsed */}
          {!isMobile && !sidebarOpen && (
            <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <BarChart2 className="h-5 w-5 text-primary-foreground" />
            </div>
              <div className={cn(
                "font-bold text-foreground",
                isLargeDesktop && "text-xl",
                isExtraLargeDesktop && "text-2xl"
              )}>
                Kaspi Price
              </div>
            </div>
          )}

          {/* Breadcrumb for large screens */}
          {(isLargeDesktop || isExtraLargeDesktop) && (
            <div className="hidden lg:flex items-center gap-1 text-sm text-muted-foreground">
              
              <span>/</span>
              <span className="text-foreground font-medium">{currentModuleName}</span>
            </div>
          )}
        </div>
        
        <div className="flex items-center gap-2 md:gap-4">
          {/* Theme Toggle */}
          <ThemeToggle />
          
          {/* Global Store Selector - only show in dashboard */}
          {user && (
            <GlobalStoreSelector />
          )}

          {/* Notifications for large screens */}
          {(isLargeDesktop || isExtraLargeDesktop) && (
            <Button variant="ghost" size="icon" className="relative">
              <Bell className="h-5 w-5" />
              <Badge className="absolute -top-1 -right-1 h-5 w-5 rounded-full p-0 flex items-center justify-center text-xs bg-red-500">
                0
              </Badge>
            </Button>
          )}
          
          {/* Help button for desktop */}
          {!isMobile && (
            <Button variant="outline" size="sm" className="hidden md:flex" onClick={handleHelpClick}>
              <HelpCircle className="h-4 w-4 mr-2" />
              Поддержка
            </Button>
          )}
          
          {user ? (
            <div className="flex gap-2">
              {/* User menu for large screens */}
              {(isLargeDesktop || isExtraLargeDesktop) && (
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" className="flex items-center gap-2" onClick={handleProfileClick}>
                      <Avatar className="h-8 w-8">
                        <AvatarImage src={profile?.avatar_url || ''} alt="Avatar" />
                        <AvatarFallback className="bg-primary text-primary-foreground text-sm">
                          {getInitials() || <User className="h-4 w-4" />}
                        </AvatarFallback>
                      </Avatar>
                      <div className="hidden xl:block text-left">
                        <div className="text-sm font-medium">{profile?.full_name || user.email?.split('@')[0]}</div>
                        <div className="text-xs text-muted-foreground">Активный пользователь</div>
                      </div>
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent 
                    align="end" 
                    className="w-56 bg-background border border-border shadow-lg z-[9999]"
                    sideOffset={5}
                  >
                    <DropdownMenuLabel>Мой аккаунт</DropdownMenuLabel>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem className="cursor-pointer" onClick={handleProfileClick}>
                      <User className="mr-2 h-4 w-4" />
                      <span>Профиль</span>
                    </DropdownMenuItem>
                    <DropdownMenuItem className="cursor-pointer" onClick={handleProfileClick}>
                      <Settings className="mr-2 h-4 w-4" />
                      <span>Настройки</span>
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem onClick={handleSignOut} className="cursor-pointer">
                      <LogOut className="mr-2 h-4 w-4" />
                      <span>Выйти</span>
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              )}

              {/* Compact user info for smaller screens */}
              {!(isLargeDesktop || isExtraLargeDesktop) && user && !isMobile && (
                <Button variant="ghost" className="flex items-center gap-2" onClick={handleProfileClick}>
                  <Avatar className="h-6 w-6">
                    <AvatarImage src={profile?.avatar_url || ''} alt="Avatar" />
                    <AvatarFallback className="bg-primary text-primary-foreground text-xs">
                      {getInitials() || <User className="h-3 w-3" />}
                    </AvatarFallback>
                  </Avatar>
                  <span className="hidden lg:inline text-sm">{profile?.full_name || user.email?.split('@')[0]}</span>
                </Button>
              )}

              {/* Mobile avatar */}
              {isMobile && user && (
                <Button variant="ghost" size="sm" onClick={handleProfileClick}>
                  <Avatar className="h-6 w-6">
                    <AvatarImage src={profile?.avatar_url || ''} alt="Avatar" />
                    <AvatarFallback className="bg-primary text-primary-foreground text-xs">
                      {getInitials() || <User className="h-3 w-3" />}
                    </AvatarFallback>
                  </Avatar>
                </Button>
              )}
            </div>
          ) : (
            <Button size="sm" variant="default" asChild>
              <Link to="/dashboard/price-bot">
                <LogIn className="mr-1 md:mr-2 h-4 w-4" />
                <span className="hidden sm:inline">Панель</span>
              </Link>
            </Button>
          )}
        </div>
      </header>
      
      <UserProfileModal 
        isOpen={isProfileModalOpen}
        onClose={() => setIsProfileModalOpen(false)}
      />
    </>
  );
};

export default Header;
