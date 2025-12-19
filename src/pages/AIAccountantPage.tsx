// Страница AI-Бухгалтера

import { AIChatInterface } from '@/components/ai-assistants/AIChatInterface';
import { aiAccountantService } from '@/services/aiAccountantService';
import { toast } from 'sonner';
import type { ChatMessage, ChatFile } from '@/types/ai-assistants';

function AIAccountantPage() {
  const handleSendMessage = async (message: string, files?: ChatFile[]): Promise<ChatMessage> => {
    try {
      const filesToSend = files?.map(f => ({
        name: f.name,
        type: f.type,
        data: f.data || '',
      }));
      
      const response = await aiAccountantService.askQuestion(
        {
          question: message,
        },
        filesToSend
      );

      const chatMessage: ChatMessage = {
        id: Date.now().toString(),
        role: 'assistant',
        content: response.answer,
        timestamp: response.timestamp || new Date().toISOString(),
        sources: response.sources,
        confidence: response.confidence,
      };

      return chatMessage;
    } catch (error: any) {
      toast.error(error.message || 'Ошибка при обращении к AI-бухгалтеру');
      throw error;
    }
  };

  const initialMessages: ChatMessage[] = [
    {
      id: 'welcome',
      role: 'assistant',
      content: 'Здравствуйте! Я AI-Бухгалтер, специализирующийся на налогообложении в Казахстане и работе с маркетплейсом Kaspi.kz.\n\nЯ могу помочь вам с:\n• Вопросами по налогам\n• Расчетом налогов\n• Отчетностью\n• Спецификой работы с Kaspi\n\nЗадайте ваш вопрос!',
      timestamp: new Date().toISOString(),
    },
  ];

  return (
    <div className="container mx-auto p-4 h-[calc(100vh-120px)]">
      <div className="h-full">
        <AIChatInterface
          title="AI-Бухгалтер"
          placeholder="Задайте вопрос по налогам, расчетам или отчетности..."
          onSendMessage={handleSendMessage}
          initialMessages={initialMessages}
          chatId="ai-accountant"
        />
      </div>
    </div>
  );
}

export default AIAccountantPage;

