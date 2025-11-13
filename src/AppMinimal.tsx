import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

// Минимальные страницы без импортов сложных компонентов
const PriceBotMinimal = () => (
  <div className="p-6 bg-white min-h-screen">
    <h1 className="text-3xl font-bold mb-6">Прайс-бот</h1>
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <div className="bg-blue-50 p-4 rounded-lg border">
        <h3 className="text-sm text-gray-600 mb-2">Всего товаров</h3>
        <p className="text-2xl font-bold text-blue-600">5</p>
      </div>
      <div className="bg-green-50 p-4 rounded-lg border">
        <h3 className="text-sm text-gray-600 mb-2">Активные</h3>
        <p className="text-2xl font-bold text-green-600">3</p>
      </div>
      <div className="bg-red-50 p-4 rounded-lg border">
        <h3 className="text-sm text-gray-600 mb-2">Неактивные</h3>
        <p className="text-2xl font-bold text-red-600">2</p>
      </div>
    </div>
    <div className="bg-gray-50 p-4 rounded-lg">
      <p>Страница прайс-бота работает!</p>
    </div>
  </div>
);

const SalesMinimal = () => (
  <div className="p-6 bg-white min-h-screen">
    <h1 className="text-3xl font-bold mb-6">Мои продажи</h1>
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <div className="bg-blue-50 p-4 rounded-lg border">
        <h3 className="text-sm text-gray-600 mb-2">Выручка</h3>
        <p className="text-xl font-bold text-blue-600">1,500,000 ₸</p>
      </div>
      <div className="bg-green-50 p-4 rounded-lg border">
        <h3 className="text-sm text-gray-600 mb-2">Заказы</h3>
        <p className="text-xl font-bold text-green-600">25</p>
      </div>
      <div className="bg-purple-50 p-4 rounded-lg border">
        <h3 className="text-sm text-gray-600 mb-2">Товары</h3>
        <p className="text-xl font-bold text-purple-600">12</p>
      </div>
      <div className="bg-orange-50 p-4 rounded-lg border">
        <h3 className="text-sm text-gray-600 mb-2">Прибыль</h3>
        <p className="text-xl font-bold text-orange-600">450,000 ₸</p>
      </div>
    </div>
    <div className="bg-gray-50 p-4 rounded-lg">
      <p>Страница продаж работает!</p>
    </div>
  </div>
);

const SimpleNavigation = () => (
  <nav className="bg-white border-b shadow-sm">
    <div className="px-6 py-4">
      <div className="flex flex-wrap gap-4">
        <a 
          href="/dashboard/price-bot" 
          className="px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-md transition-colors"
        >
          Прайс-бот
        </a>
        <a 
          href="/dashboard/sales" 
          className="px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-md transition-colors"
        >
          Продажи
        </a>
        <a 
          href="/dashboard/unit-economics" 
          className="px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-md transition-colors"
        >
          Юнит-экономика
        </a>
        <a 
          href="/dashboard/preorders" 
          className="px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-md transition-colors"
        >
          Предзаказы
        </a>
      </div>
    </div>
  </nav>
);

const MinimalLayout = ({ children }: { children: React.ReactNode }) => (
  <div className="min-h-screen bg-gray-50">
    <header className="bg-white border-b shadow-sm">
      <div className="px-6 py-4">
        <h1 className="text-xl font-bold text-gray-900">Kaspi Panel</h1>
        <p className="text-sm text-gray-600">Панель управления</p>
      </div>
    </header>
    <SimpleNavigation />
    <main>{children}</main>
  </div>
);

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard/price-bot" replace />} />
        <Route path="/dashboard" element={<Navigate to="/dashboard/price-bot" replace />} />
        <Route 
          path="/dashboard/price-bot" 
          element={
            <MinimalLayout>
              <PriceBotMinimal />
            </MinimalLayout>
          } 
        />
        <Route 
          path="/dashboard/sales" 
          element={
            <MinimalLayout>
              <SalesMinimal />
            </MinimalLayout>
          } 
        />
        <Route 
          path="/dashboard/unit-economics" 
          element={
            <MinimalLayout>
              <div className="p-6 bg-white min-h-screen">
                <h1 className="text-3xl font-bold mb-4">Юнит-экономика</h1>
                <p>Страница юнит-экономики в разработке</p>
              </div>
            </MinimalLayout>
          } 
        />
        <Route 
          path="/dashboard/preorders" 
          element={
            <MinimalLayout>
              <div className="p-6 bg-white min-h-screen">
                <h1 className="text-3xl font-bold mb-4">Предзаказы</h1>
                <p>Страница предзаказов в разработке</p>
              </div>
            </MinimalLayout>
          } 
        />
        <Route path="*" element={<Navigate to="/dashboard/price-bot" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
