// layouts/SimpleDashboardLayout.tsx
// Упрощенная версия dashboard layout для диагностики

import { Outlet } from "react-router-dom";
import { StoreContextProvider } from "@/contexts/StoreContext";
import { ModuleConfigProvider } from "@/contexts/ModuleConfigContext";

const SimpleDashboardLayout = () => {
  return (
    <ModuleConfigProvider>
      <StoreContextProvider>
        <div className="min-h-screen bg-background">
          {/* Простой хедер */}
          <header className="bg-background border-b border-border h-16 flex items-center px-6">
            <h1 className="text-xl font-semibold">Kaspi Panel</h1>
          </header>
          
          {/* Основной контент */}
          <main className="p-6">
            <Outlet />
          </main>
        </div>
      </StoreContextProvider>
    </ModuleConfigProvider>
  );
};

export default SimpleDashboardLayout;
