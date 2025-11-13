// Упрощенная версия приложения для диагностики
import { useTheme } from "@/hooks/useTheme";

const SimpleApp = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <div style={{ 
      padding: '20px', 
      minHeight: '100vh',
      backgroundColor: theme === 'dark' ? '#1a1a1a' : '#ffffff',
      color: theme === 'dark' ? '#ffffff' : '#000000'
    }}>
      <h1>🚀 Диагностика приложения</h1>
      <p>Если вы видите этот текст, значит React работает!</p>
      
      <div style={{ marginTop: '20px' }}>
        <h2>Проверка темы:</h2>
        <p>Текущая тема: <strong>{theme}</strong></p>
        <button 
          onClick={toggleTheme}
          style={{
            padding: '10px 20px',
            backgroundColor: theme === 'dark' ? '#ffffff' : '#000000',
            color: theme === 'dark' ? '#000000' : '#ffffff',
            border: 'none',
            borderRadius: '5px',
            cursor: 'pointer'
          }}
        >
          Переключить тему
        </button>
      </div>

      <div style={{ marginTop: '20px' }}>
        <h2>CSS переменные:</h2>
        <div style={{ 
          padding: '10px', 
          backgroundColor: 'hsl(var(--background))',
          color: 'hsl(var(--foreground))',
          border: '1px solid hsl(var(--border))'
        }}>
          Этот блок использует CSS переменные
        </div>
      </div>

      <div style={{ marginTop: '20px' }}>
        <h2>Ссылки для тестирования:</h2>
        <ul>
          <li><a href="/dashboard/price-bot" style={{ color: theme === 'dark' ? '#60a5fa' : '#2563eb' }}>Price Bot</a></li>
          <li><a href="/dashboard/sales" style={{ color: theme === 'dark' ? '#60a5fa' : '#2563eb' }}>Sales</a></li>
          <li><a href="/dashboard/preorders" style={{ color: theme === 'dark' ? '#60a5fa' : '#2563eb' }}>Preorders</a></li>
        </ul>
      </div>
    </div>
  );
};

export default SimpleApp;
