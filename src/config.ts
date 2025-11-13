// Конфигурация API для unified-backend
export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
export const API_VERSION = 'v1';
export const API_BASE_PATH = `/api/${API_VERSION}`;

// Полный базовый URL для API
export const API_BASE_URL = `${API_URL}${API_BASE_PATH}`;

// WAHA WhatsApp эндпоинты
export const WAHA_ENDPOINTS = {
  SESSIONS: '/waha/sessions',
  TEMPLATES: '/waha/templates',
  SEND_TEST: '/waha/send-test',
  VARIABLES: '/waha/variables',
  PREVIEW: '/waha/templates/preview'
};