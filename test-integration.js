#!/usr/bin/env node
// test-integration.js
// Скрипт для тестирования интеграции unified-backend с фронтендом

const axios = require('axios');

const API_BASE_URL = 'http://localhost:8010';
const API_VERSION = 'v1';
const FULL_API_URL = `${API_BASE_URL}/api/${API_VERSION}`;

// Цвета для консоли
const colors = {
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  reset: '\x1b[0m',
  bold: '\x1b[1m'
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

async function testEndpoint(url, method = 'GET', data = null) {
  try {
    const config = {
      method,
      url,
      headers: {
        'Content-Type': 'application/json',
      },
    };
    
    if (data) {
      config.data = data;
    }

    const response = await axios(config);
    return {
      success: true,
      status: response.status,
      data: response.data,
    };
  } catch (error) {
    return {
      success: false,
      status: error.response?.status || 0,
      error: error.message,
      data: error.response?.data,
    };
  }
}

async function runTests() {
  log('\n🚀 Тестирование интеграции unified-backend', 'bold');
  log('=' * 50, 'blue');

  const tests = [
    {
      name: 'Health Check',
      url: `${API_BASE_URL}/health`,
      method: 'GET',
    },
    {
      name: 'API Documentation',
      url: `${API_BASE_URL}/docs`,
      method: 'GET',
    },
    {
      name: 'Database Health',
      url: `${API_BASE_URL}/health/database`,
      method: 'GET',
    },
    {
      name: 'Kaspi Stores (GET)',
      url: `${FULL_API_URL}/kaspi/stores?user_id=test-user`,
      method: 'GET',
    },
    {
      name: 'Products List (GET)',
      url: `${FULL_API_URL}/products?store_id=test-store`,
      method: 'GET',
    },
    {
      name: 'Sales Data (GET)',
      url: `${FULL_API_URL}/sales?store_id=test-store`,
      method: 'GET',
    },
    {
      name: 'Demper Health',
      url: `${FULL_API_URL}/demper/health`,
      method: 'GET',
    },
    {
      name: 'Proxy Status',
      url: `${FULL_API_URL}/proxy/status`,
      method: 'GET',
    },
  ];

  let passed = 0;
  let failed = 0;

  for (const test of tests) {
    log(`\n📋 Тестирование: ${test.name}`, 'yellow');
    log(`   URL: ${test.url}`, 'blue');
    
    const result = await testEndpoint(test.url, test.method);
    
    if (result.success) {
      log(`   ✅ Успешно (${result.status})`, 'green');
      if (result.data && typeof result.data === 'object') {
        log(`   📊 Ответ: ${JSON.stringify(result.data, null, 2).substring(0, 200)}...`, 'blue');
      }
      passed++;
    } else {
      log(`   ❌ Ошибка (${result.status}): ${result.error}`, 'red');
      if (result.data) {
        log(`   📊 Детали: ${JSON.stringify(result.data, null, 2).substring(0, 200)}...`, 'red');
      }
      failed++;
    }
  }

  log('\n📊 Результаты тестирования:', 'bold');
  log(`   ✅ Успешно: ${passed}`, 'green');
  log(`   ❌ Ошибки: ${failed}`, 'red');
  log(`   📈 Общий результат: ${passed}/${tests.length}`, passed === tests.length ? 'green' : 'yellow');

  if (failed > 0) {
    log('\n⚠️  Некоторые тесты не прошли. Это может быть нормально, если:', 'yellow');
    log('   - Backend не запущен', 'yellow');
    log('   - Нет данных в базе (Supabase не настроена)', 'yellow');
    log('   - Endpoints требуют аутентификации', 'yellow');
  }

  log('\n🔗 Полезные ссылки:', 'bold');
  log(`   📖 API Docs: ${API_BASE_URL}/docs`, 'blue');
  log(`   🏥 Health Check: ${API_BASE_URL}/health`, 'blue');
  log(`   🎯 Frontend: http://localhost:5173`, 'blue');
}

// Проверяем, запущен ли backend
async function checkBackendStatus() {
  try {
    const response = await axios.get(`${API_BASE_URL}/health`, { timeout: 5000 });
    log('✅ Unified Backend запущен и доступен', 'green');
    return true;
  } catch (error) {
    log('❌ Unified Backend недоступен', 'red');
    log('   Убедитесь, что backend запущен:', 'yellow');
    log('   cd /Users/hasen/demper-667-45/unified-backend', 'yellow');
    log('   python main.py', 'yellow');
    return false;
  }
}

async function main() {
  log('🔍 Проверка статуса unified-backend...', 'blue');
  
  const backendRunning = await checkBackendStatus();
  
  if (backendRunning) {
    await runTests();
  } else {
    log('\n💡 Для запуска тестов:', 'yellow');
    log('   1. Запустите unified-backend', 'yellow');
    log('   2. Запустите этот скрипт снова', 'yellow');
  }
}

// Запуск тестов
main().catch(error => {
  log(`\n💥 Критическая ошибка: ${error.message}`, 'red');
  process.exit(1);
});
