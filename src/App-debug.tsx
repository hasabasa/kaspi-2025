// Диагностическая версия приложения без сложных контекстов
import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useTheme } from "@/hooks/useTheme";

// Простые компоненты для тестирования
const SimplePage = ({ title }: { title: string }) => (
  <div style={{ padding: '20px', minHeight: '100vh' }}>
    <h1>🎯 {title}</h1>
    <p>Эта страница работает корректно!</p>
    <div style={{ marginTop: '20px' }}>
      <p>Если вы видите этот текст, значит:</p>
      <ul>
        <li>✅ React работает</li>
        <li>✅ Router работает</li>
        <li>✅ CSS переменные работают</li>
        <li>✅ Typescript компилируется</li>
      </ul>
    </div>
    <div style={{ marginTop: '20px' }}>
      <a href="/dashboard/price-bot" style={{ marginRight: '10px' }}>Price Bot</a>
      <a href="/dashboard/sales" style={{ marginRight: '10px' }}>Sales</a>
      <a href="/dashboard/preorders" style={{ marginRight: '10px' }}>Preorders</a>
    </div>
  </div>
);

const DebugApp = () => {
  // Инициализируем тему
  useTheme();

  return (
    <BrowserRouter>
      <div style={{ 
        backgroundColor: 'var(--background, #ffffff)', 
        color: 'var(--foreground, #000000)',
        minHeight: '100vh'
      }}>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard/price-bot" replace />} />
          <Route path="/dashboard/price-bot" element={<SimplePage title="Price Bot Page" />} />
          <Route path="/dashboard/sales" element={<SimplePage title="Sales Page" />} />
          <Route path="/dashboard/preorders" element={<SimplePage title="Preorders Page" />} />
          <Route path="/dashboard/unit-economics" element={<SimplePage title="Unit Economics Page" />} />
          <Route path="/dashboard/whatsapp" element={<SimplePage title="WhatsApp Page" />} />
          <Route path="/dashboard/integrations" element={<SimplePage title="Integrations Page" />} />
          <Route path="/dashboard/profile" element={<SimplePage title="Profile Page" />} />
          <Route path="*" element={<SimplePage title="404 - Page Not Found" />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
};

export default DebugApp;
