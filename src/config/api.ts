// Централизованная конфигурация API endpoints для unified-backend
// Этот файл содержит все доступные API endpoints

import { API_URL, API_BASE_PATH } from '../config';

export const API_ENDPOINTS = {
  // Kaspi endpoints
  kaspi: {
    auth: '/kaspi/auth',
    stores: '/kaspi/stores',
    storeById: (id: string) => `/kaspi/stores/${id}`,
    syncStore: (id: string) => `/kaspi/stores/${id}/sync`,
    checkSession: (id: string) => `/kaspi/stores/${id}/session`,
  },
  
  // Products endpoints
  products: {
    list: '/products',
    search: '/products/search',
    bulkUpdate: '/products/bulk-update',
    sync: '/products/sync',
  },
  
  // Sales endpoints
  sales: {
    get: '/sales',
    add: '/sales',
    bulk: '/sales/bulk',
  },
  
  // Demper endpoints
  demper: {
    start: '/demper/start',
    stop: '/demper/stop',
    pause: '/demper/pause',
    resume: '/demper/resume',
    status: (storeId: string) => `/demper/status/${storeId}`,
    statistics: (storeId: string) => `/demper/statistics/${storeId}`,
    list: '/demper/list',
    stopAll: '/demper/stop-all',
    health: '/demper/health',
  },
  
  // Proxy endpoints
  proxy: {
    status: '/proxy/status',
    statistics: '/proxy/statistics',
    health: '/proxy/health',
    add: '/proxy/add',
    remove: '/proxy/remove',
    unblock: '/proxy/unblock',
    list: '/proxy/list',
    test: (proxyId: string) => `/proxy/test/${proxyId}`,
    resetStats: '/proxy/reset-stats',
  },
  
  // Admin endpoints
  admin: {
    system: '/admin/system',
    users: '/admin/users',
    stores: '/admin/stores',
  },
  
  // Health check endpoints
  health: {
    main: '/health',
    database: '/health/database',
    supabase: '/health/supabase',
  },
  
  // AI Assistants endpoints
  aiAccountant: {
    ask: '/ai-accountant/ask',
    calculate: '/ai-accountant/calculate',
  },
  
  aiLawyer: {
    resolveDispute: '/ai-lawyer/resolve-dispute',
    analyzeContract: '/ai-lawyer/analyze-contract',
  },
};

// Вспомогательные функции для построения URL
export const buildApiUrl = (endpoint: string): string => {
  return `${API_URL}${API_BASE_PATH}${endpoint}`;
};

export const buildFullUrl = (endpoint: string): string => {
  return `${API_URL}${endpoint}`;
};
