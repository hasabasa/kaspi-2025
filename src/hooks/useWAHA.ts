// hooks/useWAHA.ts
/**
 * Custom hook для управления WAHA WhatsApp интеграцией
 */

import { useState, useEffect, useCallback } from 'react';
import { wahaService, WAHASession, WhatsAppTemplate, TemplateCreate, TemplateUpdate, TestMessage } from '../services/wahaService';
import { useStoreContext } from '../contexts/StoreContext';

export interface UseWAHAReturn {
  // Состояние сессии
  session: WAHASession | null;
  sessionStatus: 'idle' | 'connecting' | 'connected' | 'error';
  isLoading: boolean;
  error: string | null;

  // Состояние шаблонов
  templates: WhatsAppTemplate[];
  templatesLoading: boolean;
  templatesError: string | null;

  // Действия с сессией
  startSession: (phoneNumber: string) => Promise<void>;
  checkSessionStatus: () => Promise<void>;
  deleteSession: () => Promise<void>;

  // Действия с шаблонами
  createTemplate: (template: TemplateCreate) => Promise<void>;
  updateTemplate: (templateId: number, template: TemplateUpdate) => Promise<void>;
  deleteTemplate: (templateId: number) => Promise<void>;
  refreshTemplates: () => Promise<void>;

  // Тестирование
  sendTestMessage: (testMessage: TestMessage) => Promise<{ success: boolean; error?: string }>;

  // Утилиты
  clearError: () => void;
}

export const useWAHA = (): UseWAHAReturn => {
  const { selectedStore } = useStoreContext();
  const storeId = selectedStore?.id || '';

  // Состояние сессии
  const [session, setSession] = useState<WAHASession | null>(null);
  const [sessionStatus, setSessionStatus] = useState<'idle' | 'connecting' | 'connected' | 'error'>('idle');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Состояние шаблонов
  const [templates, setTemplates] = useState<WhatsAppTemplate[]>([]);
  const [templatesLoading, setTemplatesLoading] = useState(false);
  const [templatesError, setTemplatesError] = useState<string | null>(null);

  // Polling для статуса сессии
  const [pollingInterval, setPollingInterval] = useState<NodeJS.Timeout | null>(null);

  // Очистка ошибок
  const clearError = useCallback(() => {
    setError(null);
    setTemplatesError(null);
  }, []);

  // Проверка статуса сессии
  const checkSessionStatus = useCallback(async () => {
    if (!session?.session_id) return;

    try {
      const status = await wahaService.getSessionStatus(session.session_id);
      setSession(status);

      if (status.is_connected) {
        setSessionStatus('connected');
        // Останавливаем polling при успешном подключении
        if (pollingInterval) {
          clearInterval(pollingInterval);
          setPollingInterval(null);
        }
      } else if (status.status === 'connecting') {
        setSessionStatus('connecting');
      } else if (status.status === 'error') {
        setSessionStatus('error');
        setError('Ошибка подключения к WhatsApp');
      }
    } catch (err) {
      console.error('Ошибка проверки статуса сессии:', err);
      setError(err instanceof Error ? err.message : 'Неизвестная ошибка');
      setSessionStatus('error');
    }
  }, [session?.session_id, pollingInterval]);

  // Начать сессию
  const startSession = useCallback(async (phoneNumber: string) => {
    if (!storeId) {
      setError('ID магазина не найден');
      return;
    }

    setIsLoading(true);
    setError(null);
    setSessionStatus('connecting');

    try {
      const result = await wahaService.startSession(storeId, phoneNumber);
      
      setSession({
        session_id: result.session_id,
        status: 'connecting',
        is_connected: false,
        created_at: new Date().toISOString(),
        expires_at: result.expires_at,
      });

      // Начинаем polling статуса
      const interval = setInterval(checkSessionStatus, 5000);
      setPollingInterval(interval);

    } catch (err) {
      console.error('Ошибка создания сессии:', err);
      setError(err instanceof Error ? err.message : 'Неизвестная ошибка');
      setSessionStatus('error');
    } finally {
      setIsLoading(false);
    }
  }, [storeId, checkSessionStatus]);

  // Удалить сессию
  const deleteSession = useCallback(async () => {
    if (!session?.session_id) return;

    setIsLoading(true);
    setError(null);

    try {
      await wahaService.deleteSession(session.session_id);
      
      // Останавливаем polling
      if (pollingInterval) {
        clearInterval(pollingInterval);
        setPollingInterval(null);
      }

      setSession(null);
      setSessionStatus('idle');
    } catch (err) {
      console.error('Ошибка удаления сессии:', err);
      setError(err instanceof Error ? err.message : 'Неизвестная ошибка');
    } finally {
      setIsLoading(false);
    }
  }, [session?.session_id, pollingInterval]);

  // Получить шаблоны
  const refreshTemplates = useCallback(async () => {
    if (!storeId) return;

    setTemplatesLoading(true);
    setTemplatesError(null);

    try {
      const templatesList = await wahaService.getTemplates(storeId);
      setTemplates(templatesList);
    } catch (err) {
      console.error('Ошибка получения шаблонов:', err);
      setTemplatesError(err instanceof Error ? err.message : 'Неизвестная ошибка');
    } finally {
      setTemplatesLoading(false);
    }
  }, [storeId]);

  // Создать шаблон
  const createTemplate = useCallback(async (template: TemplateCreate) => {
    if (!storeId) return;

    setTemplatesLoading(true);
    setTemplatesError(null);

    try {
      await wahaService.createTemplate(storeId, template);
      await refreshTemplates(); // Обновляем список
    } catch (err) {
      console.error('Ошибка создания шаблона:', err);
      setTemplatesError(err instanceof Error ? err.message : 'Неизвестная ошибка');
    } finally {
      setTemplatesLoading(false);
    }
  }, [storeId, refreshTemplates]);

  // Обновить шаблон
  const updateTemplate = useCallback(async (templateId: number, template: TemplateUpdate) => {
    setTemplatesLoading(true);
    setTemplatesError(null);

    try {
      await wahaService.updateTemplate(templateId, template);
      await refreshTemplates(); // Обновляем список
    } catch (err) {
      console.error('Ошибка обновления шаблона:', err);
      setTemplatesError(err instanceof Error ? err.message : 'Неизвестная ошибка');
    } finally {
      setTemplatesLoading(false);
    }
  }, [refreshTemplates]);

  // Удалить шаблон
  const deleteTemplate = useCallback(async (templateId: number) => {
    setTemplatesLoading(true);
    setTemplatesError(null);

    try {
      await wahaService.deleteTemplate(templateId);
      await refreshTemplates(); // Обновляем список
    } catch (err) {
      console.error('Ошибка удаления шаблона:', err);
      setTemplatesError(err instanceof Error ? err.message : 'Неизвестная ошибка');
    } finally {
      setTemplatesLoading(false);
    }
  }, [refreshTemplates]);

  // Отправить тестовое сообщение
  const sendTestMessage = useCallback(async (testMessage: TestMessage) => {
    if (!storeId) return { success: false, error: 'ID магазина не найден' };

    try {
      const result = await wahaService.sendTestMessage(storeId, testMessage);
      return result;
    } catch (err) {
      console.error('Ошибка отправки тестового сообщения:', err);
      return {
        success: false,
        error: err instanceof Error ? err.message : 'Неизвестная ошибка'
      };
    }
  }, [storeId]);

  // Загружаем шаблоны при монтировании
  useEffect(() => {
    if (storeId) {
      refreshTemplates();
    }
  }, [storeId, refreshTemplates]);

  // Очистка polling при размонтировании
  useEffect(() => {
    return () => {
      if (pollingInterval) {
        clearInterval(pollingInterval);
      }
    };
  }, [pollingInterval]);

  return {
    // Состояние сессии
    session,
    sessionStatus,
    isLoading,
    error,

    // Состояние шаблонов
    templates,
    templatesLoading,
    templatesError,

    // Действия с сессией
    startSession,
    checkSessionStatus,
    deleteSession,

    // Действия с шаблонами
    createTemplate,
    updateTemplate,
    deleteTemplate,
    refreshTemplates,

    // Тестирование
    sendTestMessage,

    // Утилиты
    clearError,
  };
};