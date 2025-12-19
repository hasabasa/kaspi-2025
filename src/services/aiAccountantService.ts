// Сервис для работы с AI-Бухгалтером

import { API_BASE_URL } from '@/config';
import type { AIQuestion, AIAnswer, TaxCalculation, TaxCalculationResult } from '@/types/ai-assistants';

class AIAccountantService {
  private baseUrl = `${API_BASE_URL}/ai-accountant`;

  /**
   * Задать вопрос AI-бухгалтеру
   */
  async askQuestion(question: AIQuestion, files?: Array<{ name: string; type: string; data: string }>): Promise<AIAnswer> {
    try {
      // Если есть файлы, используем FormData
      if (files && files.length > 0) {
        const formData = new FormData();
        formData.append('question', question.question);
        if (question.context) {
          formData.append('context', JSON.stringify(question.context));
        }
        
        files.forEach((file, index) => {
          // Конвертируем base64 обратно в Blob для отправки
          const byteCharacters = atob(file.data.split(',')[1]);
          const byteNumbers = new Array(byteCharacters.length);
          for (let i = 0; i < byteCharacters.length; i++) {
            byteNumbers[i] = byteCharacters.charCodeAt(i);
          }
          const byteArray = new Uint8Array(byteNumbers);
          const blob = new Blob([byteArray], { type: file.type });
          formData.append(`file_${index}`, blob, file.name);
        });

        const response = await fetch(`${this.baseUrl}/ask`, {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          const error = await response.json().catch(() => ({}));
          throw new Error(error.detail || error.message || 'Ошибка при обращении к AI-бухгалтеру');
        }

        return response.json();
      }

      // Обычный JSON запрос без файлов
      const response = await fetch(`${this.baseUrl}/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(question),
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || error.message || 'Ошибка при обращении к AI-бухгалтеру');
      }

      return response.json();
    } catch (error: any) {
      console.error('Ошибка AI-бухгалтера:', error);
      throw error;
    }
  }

  /**
   * Рассчитать налоги
   */
  async calculateTax(calculation: TaxCalculation): Promise<TaxCalculationResult> {
    try {
      const response = await fetch(`${this.baseUrl}/calculate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(calculation),
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || error.message || 'Ошибка при расчете налогов');
      }

      return response.json();
    } catch (error: any) {
      console.error('Ошибка расчета налогов:', error);
      throw error;
    }
  }
}

export const aiAccountantService = new AIAccountantService();

