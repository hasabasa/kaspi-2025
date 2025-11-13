// Минимальная версия основного приложения без проблемных контекстов
import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useTheme } from "@/hooks/useTheme";

// Импортируем только основные страницы
import PriceBotPage from "./pages/PriceBotPage";
import PreordersPage from "./pages/PreordersPage";

// Создаем упрощенные версии страниц без сложных хуков
const SimplePriceBotPage = () => (
  <div className="p-6">
    <h1 className="text-3xl font-bold mb-4">Бот демпинга</h1>
    <div className="bg-card rounded-lg shadow p-6">
      <p>Модуль управления ценами</p>
      <div className="mt-4 text-sm text-gray-600">
        Это упрощенная версия без сложных контекстов для диагностики
      </div>
    </div>
  </div>
);

const SimplePreordersPage = () => (
  <div className="p-6">
    <h1 className="text-3xl font-bold mb-4">Предзаказы</h1>
    <div className="bg-card rounded-lg shadow p-6">
      <p>Модуль управления предзаказами</p>
      <div className="mt-4 text-sm text-gray-600">
        Это упрощенная версия без сложных контекстов для диагностики
      </div>
    </div>
  </div>
);

const SimpleSalesPage = () => (
  <div className="p-6">
    <h1 className="text-3xl font-bold mb-4">Мои продажи</h1>
    <div className="bg-card rounded-lg shadow p-6">
      <p>Модуль аналитики продаж</p>
      <div className="mt-4 text-sm text-gray-600">
        Это упрощенная версия без сложных контекстов для диагностики
      </div>
    </div>
  </div>
);

// Упрощенный layout без сложных контекстов
const SimpleLayout = ({ children }: { children: React.ReactNode }) => {
  const { theme, toggleTheme } = useTheme();
  
  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Простой хедер */}
      <header className="bg-card shadow-sm border-b px-6 py-4">
        <div className="flex justify-between items-center">
          <h1 className="text-xl font-bold">Mark Bot</h1>
          <div className="flex items-center gap-4">
            <button 
              onClick={toggleTheme}
              className="px-3 py-1 bg-primary text-primary-foreground rounded"
            >
              {theme === 'dark' ? '☀️' : '🌙'}
            </button>
            <nav className="flex gap-4">
              <a href="/dashboard/price-bot" className="hover:text-primary">Price Bot</a>
              <a href="/dashboard/sales" className="hover:text-primary">Sales</a>
              <a href="/dashboard/preorders" className="hover:text-primary">Preorders</a>
            </nav>
          </div>
        </div>
      </header>
      
      {/* Контент */}
      <main className="container mx-auto p-6">
        {children}
      </main>
    </div>
  );
};

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

const MinimalApp = () => {
  // Инициализируем тему
  useTheme();

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <SimpleLayout>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard/price-bot" replace />} />
            <Route path="/dashboard/price-bot" element={<SimplePriceBotPage />} />
            <Route path="/dashboard/sales" element={<SimpleSalesPage />} />
            <Route path="/dashboard/preorders" element={<SimplePreordersPage />} />
            <Route path="*" element={<div className="text-center py-12"><h2 className="text-2xl">404 - Страница не найдена</h2></div>} />
          </Routes>
        </SimpleLayout>
      </BrowserRouter>
    </QueryClientProvider>
  );
};

export default MinimalApp;
