// Сервис для работы с AI-Юристом

import { API_BASE_URL } from '@/config';
import type { DisputeRequest, DisputeResolution } from '@/types/ai-assistants';

class AILawyerService {
  private baseUrl = `${API_BASE_URL}/ai-lawyer`;

  /**
   * Решить спорную ситуацию
   */
  async resolveDispute(dispute: DisputeRequest, files?: Array<{ name: string; type: string; data: string }>): Promise<DisputeResolution> {
    try {
      // Если есть файлы, используем FormData
      if (files && files.length > 0) {
        const formData = new FormData();
        formData.append('dispute_type', dispute.dispute_type);
        formData.append('situation', JSON.stringify(dispute.situation));
        if (dispute.context) {
          formData.append('context', JSON.stringify(dispute.context));
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

        const response = await fetch(`${this.baseUrl}/resolve-dispute`, {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          const error = await response.json().catch(() => ({}));
          throw new Error(error.detail || error.message || 'Ошибка при обращении к AI-юристу');
        }

        return response.json();
      }

      // Обычный JSON запрос без файлов
      const response = await fetch(`${this.baseUrl}/resolve-dispute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(dispute),
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || error.message || 'Ошибка при обращении к AI-юристу');
      }

      return response.json();
    } catch (error: any) {
      console.error('Ошибка AI-юриста:', error);
      throw error;
    }
  }

  /**
   * Проанализировать договор
   */
  async analyzeContract(contractText: string, contractType: string = 'kaspi_agreement'): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/analyze-contract`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          contract_text: contractText,
          contract_type: contractType,
        }),
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || error.message || 'Ошибка при анализе договора');
      }

      return response.json();
    } catch (error: any) {
      console.error('Ошибка анализа договора:', error);
      throw error;
    }
  }
}

export const aiLawyerService = new AILawyerService();

