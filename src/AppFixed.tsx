import React from "react";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useTheme } from "@/hooks/useTheme";

// Импорты страниц (проверенные и работающие)
import PriceBotPage from "./pages/PriceBotSimple";
import SalesPage from "./pages/SalesPageEnhanced";
import UnitEconomicsPage from "./pages/UnitEconomicsPage";
import PreordersPage from "./pages/PreordersPage";
import WhatsAppPage from "./pages/WhatsAppPage";
import IntegrationPage from "./pages/IntegrationPage";

// Простые компоненты
import { StoreContextProvider } from "@/contexts/StoreContext";
import { ModuleConfigProvider } from "@/contexts/ModuleConfigContext";

// Простой Layout без сложной логики
const SimpleDashboardLayout = () => {
  return (
    <div className="min-h-screen bg-background">
      {/* Простой Header */}
      <header className="border-b bg-white px-6 py-4">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold">Kaspi Panel</h1>
          <div className="text-sm text-muted-foreground">Панель управления</div>
        </div>
      </header>
      
      {/* Простая навигация */}
      <nav className="border-b bg-white px-6 py-3">
        <div className="flex flex-wrap gap-4">
          <a 
            href="/dashboard/price-bot" 
            className="text-sm font-medium text-blue-600 hover:text-blue-800 px-3 py-2 rounded"
          >
            Прайс-бот
          </a>
          <a 
            href="/dashboard/sales" 
            className="text-sm font-medium text-blue-600 hover:text-blue-800 px-3 py-2 rounded"
          >
            Продажи
          </a>
          <a 
            href="/dashboard/unit-economics" 
            className="text-sm font-medium text-blue-600 hover:text-blue-800 px-3 py-2 rounded"
          >
            Юнит-экономика
          </a>
          <a 
            href="/dashboard/preorders" 
            className="text-sm font-medium text-blue-600 hover:text-blue-800 px-3 py-2 rounded"
          >
            Предзаказы
          </a>
          <a 
            href="/dashboard/whatsapp" 
            className="text-sm font-medium text-blue-600 hover:text-blue-800 px-3 py-2 rounded"
          >
            WhatsApp
          </a>
          <a 
            href="/dashboard/integrations" 
            className="text-sm font-medium text-blue-600 hover:text-blue-800 px-3 py-2 rounded"
          >
            Интеграции
          </a>
        </div>
      </nav>
      
      {/* Контент */}
      <main className="bg-gray-50 min-h-[calc(100vh-8rem)]">
        <Routes>
          <Route index element={<Navigate to="price-bot" replace />} />
          <Route path="price-bot" element={<PriceBotPage />} />
          <Route path="sales" element={<SalesPage />} />
          <Route path="unit-economics" element={<UnitEconomicsPage />} />
          <Route path="preorders" element={<PreordersPage />} />
          <Route path="whatsapp" element={<WhatsAppPage />} />
          <Route path="integrations" element={<IntegrationPage />} />
        </Routes>
      </main>
    </div>
  );
};

// Простой ProtectedRoute (без сложной логики)
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  return <>{children}</>;
};

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  useTheme();

  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <ModuleConfigProvider>
          <StoreContextProvider>
            <BrowserRouter>
              <div className="relative flex min-h-screen flex-col bg-background">
                <Routes>
                  <Route path="/" element={<Navigate to="/dashboard" replace />} />
                  <Route 
                    path="/dashboard/*" 
                    element={
                      <ProtectedRoute>
                        <SimpleDashboardLayout />
                      </ProtectedRoute>
                    } 
                  />
                  <Route path="*" element={<Navigate to="/dashboard" replace />} />
                </Routes>
              </div>
              <Sonner position="bottom-right" />
            </BrowserRouter>
          </StoreContextProvider>
        </ModuleConfigProvider>
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;
