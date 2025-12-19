// Хук для управления историей чатов

import { useState, useEffect } from 'react';
import type { ChatMessage } from '@/types/ai-assistants';

const STORAGE_PREFIX = 'ai_chat_history_';

export function useChatHistory(chatId: string, initialMessages: ChatMessage[] = []) {
  const storageKey = `${STORAGE_PREFIX}${chatId}`;

  const [messages, setMessages] = useState<ChatMessage[]>(() => {
    // Загружаем из localStorage при инициализации
    try {
      const saved = localStorage.getItem(storageKey);
      if (saved) {
        const parsed = JSON.parse(saved);
        // Объединяем с начальными сообщениями (приветствие)
        return [...initialMessages, ...parsed];
      }
    } catch (error) {
      console.error('Ошибка загрузки истории чата:', error);
    }
    return initialMessages;
  });

  // Сохраняем в localStorage при изменении
  useEffect(() => {
    try {
      // Сохраняем только сообщения после начальных (приветствие)
      const messagesToSave = messages.slice(initialMessages.length);
      if (messagesToSave.length > 0) {
        localStorage.setItem(storageKey, JSON.stringify(messagesToSave));
      }
    } catch (error) {
      console.error('Ошибка сохранения истории чата:', error);
    }
  }, [messages, storageKey, initialMessages.length]);

  const addMessage = (message: ChatMessage) => {
    setMessages((prev) => [...prev, message]);
  };

  const clearHistory = () => {
    setMessages(initialMessages);
    localStorage.removeItem(storageKey);
  };

  return {
    messages,
    setMessages,
    addMessage,
    clearHistory,
  };
}


