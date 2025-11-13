import { Link, useLocation } from "react-router-dom";
import { cn } from "@/lib/utils";
import { 
  TrendingUp, 
  BarChart3, 
  Calculator, 
  ShoppingBag, 
  MessageSquare, 
  Zap, 
  Menu 
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useScreenSize } from "@/hooks/use-screen-size";
import {
  Drawer,
  DrawerContent,
  DrawerHeader,
  DrawerTitle,
} from "@/components/ui/drawer";

interface SidebarProps {
  isOpen: boolean;
  setIsOpen: (isOpen: boolean) => void;
  width?: string;
}

const Sidebar = ({ isOpen, setIsOpen, width }: SidebarProps) => {
  const location = useLocation();
  const { isMobile } = useScreenSize();

  if (isMobile) {
    return (
      <Drawer open={isOpen} onOpenChange={setIsOpen}>
        <DrawerContent className="h-[85vh]">
          <DrawerHeader className="border-b">
            <DrawerTitle className="text-xl font-bold text-center">Панель управления</DrawerTitle>
          </DrawerHeader>
          <div className="flex-1 overflow-y-auto p-4">
            <nav className="space-y-2">
              <Link to="/dashboard/price-bot" className="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800">
                <TrendingUp className="h-5 w-5" />
                <span>Бот демпинга</span>
              </Link>
              <Link to="/dashboard/sales" className="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800">
                <BarChart3 className="h-5 w-5" />
                <span>Мои продажи</span>
              </Link>
              <Link to="/dashboard/unit-economics" className="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800">
                <Calculator className="h-5 w-5" />
                <span>Юнит-экономика</span>
              </Link>
              <Link to="/dashboard/preorders" className="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800">
                <ShoppingBag className="h-5 w-5" />
                <span>Предзаказы</span>
              </Link>
              <Link to="/dashboard/whatsapp" className="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800">
                <MessageSquare className="h-5 w-5" />
                <span>WhatsApp</span>
              </Link>
              <Link to="/dashboard/integrations" className="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800">
                <Zap className="h-5 w-5" />
                <span>Интеграции</span>
              </Link>
            </nav>
          </div>
        </DrawerContent>
      </Drawer>
    );
  }

  return (
    <section 
      id="sidebar"
      className={cn(
        "fixed top-0 left-0 z-40 h-full transition-all duration-300 ease-in-out overflow-x-hidden font-['Lato',sans-serif]",
        isOpen ? "w-[220px]" : "w-[60px]"
      )}
    >
      {/* Top Menu - без brand секции */}
      <ul className="side-menu top" style={{ marginTop: '48px' }}>
        <li className={location.pathname === "/dashboard/price-bot" ? "active" : ""}>
          <Link to="/dashboard/price-bot">
            <TrendingUp className="text-base" />
            <span className="text">Бот демпинга</span>
          </Link>
        </li>
        <li className={location.pathname === "/dashboard/sales" ? "active" : ""}>
          <Link to="/dashboard/sales">
            <BarChart3 className="text-base" />
            <span className="text">Мои продажи</span>
          </Link>
        </li>
        <li className={location.pathname === "/dashboard/unit-economics" ? "active" : ""}>
          <Link to="/dashboard/unit-economics">
            <Calculator className="text-base" />
            <span className="text">Юнит-экономика</span>
          </Link>
        </li>
        <li className={location.pathname === "/dashboard/preorders" ? "active" : ""}>
          <Link to="/dashboard/preorders">
            <ShoppingBag className="text-base" />
            <span className="text">Предзаказы</span>
          </Link>
        </li>
        <li className={location.pathname === "/dashboard/whatsapp" ? "active" : ""}>
          <Link to="/dashboard/whatsapp">
            <MessageSquare className="text-base" />
            <span className="text">WhatsApp</span>
          </Link>
        </li>
        <li className={location.pathname === "/dashboard/integrations" ? "active" : ""}>
          <Link to="/dashboard/integrations">
            <Zap className="text-base" />
            <span className="text">Интеграции</span>
          </Link>
        </li>
      </ul>

      {/* Bottom Menu - удален */}
    </section>
  );
};

// Обработчик для переключения сайдбара
const MenuToggle = ({ isOpen, setIsOpen }: { isOpen: boolean; setIsOpen: (open: boolean) => void }) => {
  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={() => setIsOpen(!isOpen)}
      className="p-0 h-auto min-h-0 text-foreground hover:text-blue-600 dark:hover:text-blue-400"
    >
      <Menu className="h-5 w-5" />
    </Button>
  );
};

export { MenuToggle };
export default Sidebar;