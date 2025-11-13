import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

// Рабочие компоненты прайс-бота
const PriceBotFunctional = () => {
  const products = [
    { id: 1, name: "iPhone 15 Pro Max 256GB", price: 650000, active: true },
    { id: 2, name: "Samsung Galaxy S24 Ultra", price: 580000, active: false },
    { id: 3, name: "MacBook Air M2", price: 899000, active: true },
  ];

  const activeCount = products.filter(p => p.active).length;
  const inactiveCount = products.length - activeCount;

  return (
    <div className="p-4 md:p-6 bg-white min-h-screen">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-2xl md:text-3xl font-bold mb-6">Прайс-бот</h1>
        <p className="text-gray-600 mb-6">Простое управление ценами на ваши товары</p>
        
        {/* Статистика */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="bg-blue-50 p-4 rounded-lg border">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold">📦</span>
              </div>
              <div>
                <div className="text-2xl font-bold text-blue-600">{products.length}</div>
                <div className="text-sm text-gray-600">Всего товаров</div>
              </div>
            </div>
          </div>
          
          <div className="bg-green-50 p-4 rounded-lg border">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-green-500 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold">✅</span>
              </div>
              <div>
                <div className="text-2xl font-bold text-green-600">{activeCount}</div>
                <div className="text-sm text-gray-600">Бот активен</div>
              </div>
            </div>
          </div>
          
          <div className="bg-red-50 p-4 rounded-lg border">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-red-500 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold">❌</span>
              </div>
              <div>
                <div className="text-2xl font-bold text-red-600">{inactiveCount}</div>
                <div className="text-sm text-gray-600">Бот неактивен</div>
              </div>
            </div>
          </div>
        </div>

        {/* Товары */}
        <div className="bg-white border rounded-lg">
          <div className="p-4 border-b">
            <h2 className="text-lg font-semibold">Товары ({products.length})</h2>
          </div>
          <div className="p-4">
            <div className="space-y-4">
              {products.map((product) => (
                <div key={product.id} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center">
                      <span className="text-gray-400">📱</span>
                    </div>
                    <div>
                      <h3 className="font-medium text-sm md:text-base">{product.name}</h3>
                      <p className="text-gray-600 text-sm">Цена: {product.price.toLocaleString()} ₸</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                      product.active 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {product.active ? 'Активен' : 'Неактивен'}
                    </span>
                    <button 
                      className={`px-4 py-2 rounded text-sm font-medium transition-colors ${
                        product.active
                          ? 'bg-red-500 hover:bg-red-600 text-white'
                          : 'bg-green-500 hover:bg-green-600 text-white'
                      }`}
                    >
                      {product.active ? 'Выключить' : 'Включить'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Рабочие компоненты продаж
const SalesFunctional = () => {
  const salesData = {
    revenue: 2500000,
    orders: 47,
    products: 18,
    profit: 750000
  };

  return (
    <div className="p-4 md:p-6 bg-white min-h-screen">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-2xl md:text-3xl font-bold mb-6">Мои продажи</h1>
        <p className="text-gray-600 mb-6">Анализ ваших продаж на Kaspi.kz</p>
        
        {/* Метрики */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <div className="bg-blue-50 p-4 rounded-lg border">
            <div className="flex items-center gap-3">
              <span className="text-2xl">💰</span>
              <div>
                <div className="text-lg md:text-xl font-bold text-blue-600">
                  {salesData.revenue.toLocaleString()} ₸
                </div>
                <div className="text-xs md:text-sm text-gray-600">Общая выручка</div>
              </div>
            </div>
          </div>
          
          <div className="bg-green-50 p-4 rounded-lg border">
            <div className="flex items-center gap-3">
              <span className="text-2xl">📦</span>
              <div>
                <div className="text-lg md:text-xl font-bold text-green-600">{salesData.orders}</div>
                <div className="text-xs md:text-sm text-gray-600">Заказы</div>
              </div>
            </div>
          </div>
          
          <div className="bg-purple-50 p-4 rounded-lg border">
            <div className="flex items-center gap-3">
              <span className="text-2xl">🛍️</span>
              <div>
                <div className="text-lg md:text-xl font-bold text-purple-600">{salesData.products}</div>
                <div className="text-xs md:text-sm text-gray-600">Товары</div>
              </div>
            </div>
          </div>
          
          <div className="bg-orange-50 p-4 rounded-lg border">
            <div className="flex items-center gap-3">
              <span className="text-2xl">📈</span>
              <div>
                <div className="text-lg md:text-xl font-bold text-orange-600">
                  {salesData.profit.toLocaleString()} ₸
                </div>
                <div className="text-xs md:text-sm text-gray-600">Прибыль</div>
              </div>
            </div>
          </div>
        </div>

        {/* График заглушка */}
        <div className="bg-gray-50 p-8 rounded-lg border text-center">
          <span className="text-4xl mb-4 block">📊</span>
          <h3 className="text-lg font-medium mb-2">График продаж</h3>
          <p className="text-gray-600">Здесь будет отображаться динамика продаж</p>
        </div>
      </div>
    </div>
  );
};

// Простая навигация
const Navigation = () => (
  <nav className="bg-white border-b shadow-sm">
    <div className="px-4 md:px-6 py-4">
      <div className="flex flex-wrap gap-2 md:gap-4">
        <a 
          href="/dashboard/price-bot" 
          className="px-3 md:px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-md transition-colors"
        >
          Прайс-бот
        </a>
        <a 
          href="/dashboard/sales" 
          className="px-3 md:px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-md transition-colors"
        >
          Продажи
        </a>
        <a 
          href="/dashboard/unit-economics" 
          className="px-3 md:px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-md transition-colors"
        >
          Юнит-экономика
        </a>
        <a 
          href="/dashboard/preorders" 
          className="px-3 md:px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-md transition-colors"
        >
          Предзаказы
        </a>
        <a 
          href="/dashboard/whatsapp" 
          className="px-3 md:px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-md transition-colors"
        >
          WhatsApp
        </a>
        <a 
          href="/dashboard/integrations" 
          className="px-3 md:px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-md transition-colors"
        >
          Интеграции
        </a>
      </div>
    </div>
  </nav>
);

const Layout = ({ children }: { children: React.ReactNode }) => (
  <div className="min-h-screen bg-gray-50">
    <header className="bg-white border-b shadow-sm">
      <div className="px-4 md:px-6 py-4">
        <h1 className="text-xl font-bold text-gray-900">Kaspi Panel</h1>
        <p className="text-sm text-gray-600">Панель управления магазином</p>
      </div>
    </header>
    <Navigation />
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
            <Layout>
              <PriceBotFunctional />
            </Layout>
          } 
        />
        <Route 
          path="/dashboard/sales" 
          element={
            <Layout>
              <SalesFunctional />
            </Layout>
          } 
        />
        <Route 
          path="/dashboard/unit-economics" 
          element={
            <Layout>
              <div className="p-6 bg-white min-h-screen">
                <h1 className="text-3xl font-bold mb-4">Юнит-экономика</h1>
                <div className="bg-gray-50 p-8 rounded-lg border text-center">
                  <span className="text-4xl mb-4 block">🧮</span>
                  <p>Калькулятор прибыльности товаров</p>
                </div>
              </div>
            </Layout>
          } 
        />
        <Route 
          path="/dashboard/preorders" 
          element={
            <Layout>
              <div className="p-6 bg-white min-h-screen">
                <h1 className="text-3xl font-bold mb-4">Предзаказы</h1>
                <div className="bg-gray-50 p-8 rounded-lg border text-center">
                  <span className="text-4xl mb-4 block">📋</span>
                  <p>Управление предзаказами товаров</p>
                </div>
              </div>
            </Layout>
          } 
        />
        <Route 
          path="/dashboard/whatsapp" 
          element={
            <Layout>
              <div className="p-6 bg-white min-h-screen">
                <h1 className="text-3xl font-bold mb-4">WhatsApp</h1>
                <div className="bg-gray-50 p-8 rounded-lg border text-center">
                  <span className="text-4xl mb-4 block">💬</span>
                  <p>Интеграция с WhatsApp</p>
                </div>
              </div>
            </Layout>
          } 
        />
        <Route 
          path="/dashboard/integrations" 
          element={
            <Layout>
              <div className="p-6 bg-white min-h-screen">
                <h1 className="text-3xl font-bold mb-4">Интеграции</h1>
                <div className="bg-gray-50 p-8 rounded-lg border text-center">
                  <span className="text-4xl mb-4 block">🔗</span>
                  <p>Подключение магазинов Kaspi.kz</p>
                </div>
              </div>
            </Layout>
          } 
        />
        <Route path="*" element={<Navigate to="/dashboard/price-bot" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
