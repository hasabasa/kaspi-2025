import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

// Простые страницы для тестирования
const TestPage = () => (
  <div className="p-6">
    <h1 className="text-2xl font-bold">Тест страница</h1>
    <p>Приложение работает!</p>
  </div>
);

const PriceBotTestPage = () => (
  <div className="p-6">
    <h1 className="text-2xl font-bold">Прайс-бот</h1>
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
      <div className="border p-4 rounded">
        <h3>Всего товаров</h3>
        <p className="text-2xl font-bold">5</p>
      </div>
      <div className="border p-4 rounded">
        <h3>Активные</h3>
        <p className="text-2xl font-bold text-green-600">3</p>
      </div>
      <div className="border p-4 rounded">
        <h3>Неактивные</h3>
        <p className="text-2xl font-bold text-red-600">2</p>
      </div>
    </div>
  </div>
);

const SalesTestPage = () => (
  <div className="p-6">
    <h1 className="text-2xl font-bold">Мои продажи</h1>
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-4">
      <div className="border p-4 rounded">
        <h3>Выручка</h3>
        <p className="text-xl font-bold">1,500,000 ₸</p>
      </div>
      <div className="border p-4 rounded">
        <h3>Заказы</h3>
        <p className="text-xl font-bold">25</p>
      </div>
      <div className="border p-4 rounded">
        <h3>Товары</h3>
        <p className="text-xl font-bold">12</p>
      </div>
      <div className="border p-4 rounded">
        <h3>Прибыль</h3>
        <p className="text-xl font-bold">450,000 ₸</p>
      </div>
    </div>
  </div>
);

// Простой Layout
const SimpleLayout = ({ children }: { children: React.ReactNode }) => (
  <div className="min-h-screen bg-gray-50">
    {/* Простой Header */}
    <header className="bg-white shadow-sm border-b">
      <div className="px-6 py-4">
        <h1 className="text-xl font-bold">Kaspi Panel</h1>
      </div>
    </header>
    
    {/* Простая навигация */}
    <nav className="bg-white border-b p-4">
      <div className="flex space-x-4">
        <a href="/dashboard/price-bot" className="text-blue-600 hover:text-blue-800">Прайс-бот</a>
        <a href="/dashboard/sales" className="text-blue-600 hover:text-blue-800">Продажи</a>
        <a href="/dashboard/unit-economics" className="text-blue-600 hover:text-blue-800">Юнит-экономика</a>
        <a href="/dashboard/preorders" className="text-blue-600 hover:text-blue-800">Предзаказы</a>
      </div>
    </nav>
    
    {/* Контент */}
    <main>{children}</main>
  </div>
);

function AppSimple() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard/price-bot" replace />} />
        <Route path="/dashboard" element={<Navigate to="/dashboard/price-bot" replace />} />
        <Route 
          path="/dashboard/price-bot" 
          element={
            <SimpleLayout>
              <PriceBotTestPage />
            </SimpleLayout>
          } 
        />
        <Route 
          path="/dashboard/sales" 
          element={
            <SimpleLayout>
              <SalesTestPage />
            </SimpleLayout>
          } 
        />
        <Route 
          path="/dashboard/unit-economics" 
          element={
            <SimpleLayout>
              <TestPage />
            </SimpleLayout>
          } 
        />
        <Route 
          path="/dashboard/preorders" 
          element={
            <SimpleLayout>
              <TestPage />
            </SimpleLayout>
          } 
        />
        <Route path="*" element={<TestPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default AppSimple;
