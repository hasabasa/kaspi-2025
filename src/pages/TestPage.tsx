// pages/TestPage.tsx
// Простая тестовая страница для проверки работоспособности

import React from 'react';

export default function TestPage() {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Тестовая страница</h1>
      <p className="text-muted-foreground">
        Эта страница работает! Значит проблема была в сложных компонентах.
      </p>
      
      <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-4 border rounded-lg">
          <h2 className="font-semibold">Десктоп версия</h2>
          <p className="text-sm text-muted-foreground">Все работает</p>
        </div>
        
        <div className="p-4 border rounded-lg">
          <h2 className="font-semibold">Мобильная версия</h2>
          <p className="text-sm text-muted-foreground">Тоже работает</p>
        </div>
      </div>
    </div>
  );
}
