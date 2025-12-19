// Страница AI-Юриста

import { AIChatInterface } from '@/components/ai-assistants/AIChatInterface';
import { aiLawyerService } from '@/services/aiLawyerService';
import { toast } from 'sonner';
import type { ChatMessage, ChatFile } from '@/types/ai-assistants';

function AILawyerPage() {
  const handleSendMessage = async (message: string, files?: ChatFile[]): Promise<ChatMessage> => {
    try {
      // Определяем тип спора из сообщения (простая эвристика)
      let disputeType: 'return' | 'exchange' | 'complaint' | 'kaspi_violation' | 'other' = 'other';
      
      const lowerMessage = message.toLowerCase();
      if (lowerMessage.includes('возврат') || lowerMessage.includes('вернуть')) {
        disputeType = 'return';
      } else if (lowerMessage.includes('обмен')) {
        disputeType = 'exchange';
      } else if (lowerMessage.includes('жалоб') || lowerMessage.includes('претензи')) {
        disputeType = 'complaint';
      } else if (lowerMessage.includes('kaspi') && (lowerMessage.includes('наруш') || lowerMessage.includes('правил'))) {
        disputeType = 'kaspi_violation';
      }

      const filesToSend = files?.map(f => ({
        name: f.name,
        type: f.type,
        data: f.data || '',
      }));

      const response = await aiLawyerService.resolveDispute(
        {
          dispute_type: disputeType,
          situation: {
            description: message,
          },
        },
        filesToSend
      );

      const chatMessage: ChatMessage = {
        id: Date.now().toString(),
        role: 'assistant',
        content: `${response.analysis}\n\n${response.recommendations.length > 0 ? 'Рекомендации:\n' + response.recommendations.map((r, i) => `${i + 1}. ${r}`).join('\n') : ''}`,
        timestamp: response.timestamp || new Date().toISOString(),
        sources: response.legal_basis?.map((basis) => ({
          text: basis.text,
          source: basis.source,
        })),
        confidence: response.confidence,
      };

      return chatMessage;
    } catch (error: any) {
      toast.error(error.message || 'Ошибка при обращении к AI-юристу');
      throw error;
    }
  };

  const initialMessages: ChatMessage[] = [
    {
      id: 'welcome',
      role: 'assistant',
      content: 'Здравствуйте! Я AI-Юрист, специализирующийся на защите прав продавцов на маркетплейсе Kaspi.kz в Казахстане.\n\nЯ могу помочь вам с:\n• Решением спорных ситуаций с покупателями\n• Защитой прав продавца\n• Анализом договоров и правил Kaspi\n• Консультациями по законодательству РК\n• Возвратами и обменами\n\nОпишите вашу ситуацию, и я помогу найти решение!',
      timestamp: new Date().toISOString(),
    },
  ];

  return (
    <div className="container mx-auto p-4 h-[calc(100vh-120px)]">
      <div className="h-full">
        <AIChatInterface
          title="AI-Юрист"
          placeholder="Опишите спорную ситуацию или задайте юридический вопрос..."
          onSendMessage={handleSendMessage}
          initialMessages={initialMessages}
          chatId="ai-lawyer"
        />
      </div>
    </div>
  );
}

export default AILawyerPage;

