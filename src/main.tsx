
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.tsx';
import './index.css';

// Global error handling for unhandled rejections
window.addEventListener('unhandledrejection', (event) => {
  console.warn('Unhandled promise rejection:', event.reason);
  // Prevent default handling for non-critical errors
  if (event.reason?.message?.includes('unload is not allowed')) {
    event.preventDefault();
  }
});

// Global error handling for module loading errors
window.addEventListener('error', (event) => {
  if (event.message?.includes('MIME type')) {
    console.warn('MIME type error caught and handled:', event.message);
    event.preventDefault();
  }
});

// Обеспечиваем, что корневой элемент существует
const rootElement = document.getElementById("root");
if (!rootElement) {
  const rootDiv = document.createElement("div");
  rootDiv.id = "root";
  document.body.appendChild(rootDiv);
}

// Функция для удаления initial loader
const removeInitialLoader = () => {
  const initialLoader = document.getElementById('initial-loader');
  if (initialLoader) {
    initialLoader.classList.add('fade-out');
    setTimeout(() => {
      initialLoader.remove();
    }, 500);
  }
};

try {
  console.log('🚀 Загружаем минимальное приложение');
  
  createRoot(document.getElementById("root")!).render(
    <StrictMode>
      <App />
    </StrictMode>
  );

  // Удаляем initial loader после монтирования React
  setTimeout(removeInitialLoader, 100);
} catch (error) {
  console.error('Failed to render React app:', error);
  // Fallback: show error message
  const rootEl = document.getElementById("root");
  if (rootEl) {
    rootEl.innerHTML = `
      <div style="display: flex; justify-content: center; align-items: center; height: 100vh; flex-direction: column;">
        <h1 style="color: #dc2626; margin-bottom: 1rem;">Ошибка загрузки приложения</h1>
        <p style="color: #6b7280;">Пожалуйста, перезагрузите страницу</p>
        <button onclick="window.location.reload()" style="margin-top: 1rem; padding: 0.5rem 1rem; background: #3b82f6; color: white; border: none; border-radius: 0.375rem; cursor: pointer;">
          Перезагрузить
        </button>
      </div>
    `;
  }
}
