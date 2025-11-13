
import { useState, useEffect } from "react";
import { Outlet } from "react-router-dom";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import { cn } from "@/lib/utils";
import { useScreenSize } from "@/hooks/use-screen-size";
// Временно убираем мобильные компоненты
// import { MobileSidebar } from "@/components/layout/MobileSidebar";
// import { MobileHeader } from "@/components/layout/MobileHeader";
// import { useMobileOptimizedSimple as useMobileOptimized } from "@/hooks/useMobileOptimizedSimple";
import { StoreContextProvider } from "@/contexts/StoreContext";
import { ModuleConfigProvider } from "@/contexts/ModuleConfigContext";

const DashboardLayout = () => {
  const { isMobile, isDesktop, isLargeDesktop, isExtraLargeDesktop } = useScreenSize();
  // На мобиле sidebar закрыт по умолчанию, на десктопе открыт
  const [sidebarOpen, setSidebarOpen] = useState(!isMobile);
  
  // Обновляем состояние sidebar при изменении размера экрана
  useEffect(() => {
    setSidebarOpen(!isMobile);
  }, [isMobile]);

  // AdminHub стиль - управление классом hide и активными ссылками
  useEffect(() => {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.querySelector('.main-content');
    
    if (sidebar && mainContent) {
      if (sidebarOpen) {
        sidebar.classList.remove('hide');
        mainContent.classList.remove('sidebar-collapsed');
      } else {
        sidebar.classList.add('hide');
        mainContent.classList.add('sidebar-collapsed');
      }
    }

    // Обработка активных пунктов меню как в AdminHub
    const allSideMenu = document.querySelectorAll('#sidebar .side-menu.top li a');
    allSideMenu.forEach(item => {
      const li = item.parentElement;
      
      item.addEventListener('click', function () {
        allSideMenu.forEach(i => {
          i.parentElement?.classList.remove('active');
        });
        li?.classList.add('active');
      });
    });

    // Функция для адаптации сайдбара к размеру экрана
    function adjustSidebar() {
      if (window.innerWidth <= 576) {
        sidebar?.classList.add('hide');
      } else {
        if (sidebarOpen) {
          sidebar?.classList.remove('hide');
        }
      }
    }

    // Слушатели событий
    window.addEventListener('load', adjustSidebar);
    window.addEventListener('resize', adjustSidebar);

    return () => {
      window.removeEventListener('load', adjustSidebar);
      window.removeEventListener('resize', adjustSidebar);
    };
  }, [sidebarOpen]);

  // Responsive sidebar widths
  const getSidebarWidth = () => {
    if (isMobile) return "280px";
    return sidebarOpen ? "220px" : "60px";
  };

  return (
    <ModuleConfigProvider>
      <StoreContextProvider>
        <div className="min-h-screen bg-background">
          {/* Показываем Sidebar только на десктопе, на мобиле он должен быть скрыт по умолчанию */}
          <div className={cn(
            "transition-transform duration-300 ease-in-out",
            isMobile && "fixed inset-y-0 left-0 z-50",
            isMobile && !sidebarOpen && "-translate-x-full",
            isMobile && sidebarOpen && "translate-x-0"
          )}>
            <Sidebar 
              isOpen={sidebarOpen} 
              setIsOpen={setSidebarOpen}
              width={getSidebarWidth()}
            />
          </div>
          
          {/* Оверлей для мобильного sidebar */}
          {isMobile && sidebarOpen && (
            <div 
              className="fixed inset-0 bg-black/50 z-40"
              onClick={() => setSidebarOpen(false)}
            />
          )}
          
          <div className={cn(
            "min-h-screen transition-all duration-300 ease-in-out",
            isMobile ? "w-full" : "main-content"
          )}>
            {/* Всегда показываем Header */}
            <Header 
              toggleSidebar={() => setSidebarOpen(!sidebarOpen)} 
              isMobile={isMobile}
              sidebarOpen={sidebarOpen}
            />
            
            <main className={cn(
              isMobile ? "p-4" : "p-6",
              isDesktop && "min-h-[calc(100vh-80px)]",
              isMobile && "min-h-[calc(100vh-4rem)]"
            )}>
              <div className="w-full">
                <Outlet />
              </div>
            </main>
          </div>
        </div>
      </StoreContextProvider>
    </ModuleConfigProvider>
  );
};

export default DashboardLayout;
