// Компонент чат-интерфейса для AI-ассистентов

import { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Send, Loader2, Bot, User, Trash2, Image as ImageIcon, FileText, Download } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useChatHistory } from '@/hooks/useChatHistory';
import { FileUploadButton } from './FileUploadButton';
import type { ChatMessage, ChatFile } from '@/types/ai-assistants';

interface AIChatInterfaceProps {
  title: string;
  placeholder?: string;
  onSendMessage: (message: string, files?: ChatFile[]) => Promise<ChatMessage>;
  initialMessages?: ChatMessage[];
  chatId: string; // Уникальный ID для сохранения истории
}

export function AIChatInterface({
  title,
  placeholder = 'Задайте вопрос...',
  onSendMessage,
  initialMessages = [],
  chatId,
}: AIChatInterfaceProps) {
  const { messages, setMessages, addMessage, clearHistory } = useChatHistory(chatId, initialMessages);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<ChatFile[]>([]);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if ((!input.trim() && selectedFiles.length === 0) || loading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim() || (selectedFiles.length > 0 ? `Прикреплено файлов: ${selectedFiles.length}` : ''),
      timestamp: new Date().toISOString(),
      files: selectedFiles.length > 0 ? [...selectedFiles] : undefined,
    };

    addMessage(userMessage);
    const filesToSend = [...selectedFiles];
    setInput('');
    setSelectedFiles([]);
    setLoading(true);

    try {
      const response = await onSendMessage(input.trim() || '', filesToSend);
      addMessage(response);
    } catch (error: any) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `Ошибка: ${error.message || 'Не удалось получить ответ'}`,
        timestamp: new Date().toISOString(),
      };
      addMessage(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleClearHistory = () => {
    if (confirm('Очистить историю чата?')) {
      clearHistory();
    }
  };

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="border-b flex flex-row items-center justify-between">
        <CardTitle className="flex items-center gap-2">
          <Bot className="h-5 w-5" />
          {title}
        </CardTitle>
        <Button
          variant="ghost"
          size="sm"
          onClick={handleClearHistory}
          className="text-muted-foreground"
        >
          <Trash2 className="h-4 w-4 mr-1" />
          Очистить
        </Button>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col p-0">
        <ScrollArea className="flex-1 p-4" ref={scrollAreaRef}>
          <div className="space-y-4">
            {messages.length === 0 && (
              <div className="text-center text-muted-foreground py-8">
                <Bot className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>Начните диалог, задав вопрос</p>
              </div>
            )}
            {messages.map((message) => (
              <div
                key={message.id}
                className={cn(
                  'flex gap-3',
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                )}
              >
                {message.role === 'assistant' && (
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                    <Bot className="h-4 w-4 text-primary" />
                  </div>
                )}
                <div
                  className={cn(
                    'max-w-[80%] rounded-lg px-4 py-2',
                    message.role === 'user'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted'
                  )}
                >
                  <div className="whitespace-pre-wrap break-words">{message.content}</div>
                  
                  {/* Отображение прикрепленных файлов */}
                  {message.files && message.files.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-border/50 space-y-2">
                      {message.files.map((file) => (
                        <div
                          key={file.id}
                          className={cn(
                            'flex items-center gap-2 p-2 rounded bg-background/50',
                            message.role === 'user' ? 'bg-white/10' : 'bg-background'
                          )}
                        >
                          {file.type.startsWith('image/') ? (
                            <div className="space-y-1">
                              <ImageIcon className="h-4 w-4" />
                              {file.url && (
                                <img
                                  src={file.url}
                                  alt={file.name}
                                  className="max-w-[200px] max-h-[200px] object-cover rounded"
                                />
                              )}
                            </div>
                          ) : (
                            <FileText className="h-4 w-4" />
                          )}
                          <div className="flex-1 min-w-0">
                            <p className="text-xs truncate">{file.name}</p>
                            <p className="text-xs opacity-70">
                              {(file.size / 1024).toFixed(1)} KB
                            </p>
                          </div>
                          {file.data && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => {
                                const link = document.createElement('a');
                                link.href = file.data!;
                                link.download = file.name;
                                link.click();
                              }}
                              className="h-6 w-6 p-0"
                            >
                              <Download className="h-3 w-3" />
                            </Button>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                  
                  {message.sources && message.sources.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-border/50">
                      <p className="text-xs text-muted-foreground mb-1">Источники:</p>
                      <ul className="text-xs space-y-1">
                        {message.sources.slice(0, 3).map((source, idx) => (
                          <li key={idx} className="text-muted-foreground">
                            • {source.source}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {message.confidence && (
                    <div className="mt-1 text-xs text-muted-foreground">
                      Уверенность: {Math.round(message.confidence * 100)}%
                    </div>
                  )}
                </div>
                {message.role === 'user' && (
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                    <User className="h-4 w-4 text-primary" />
                  </div>
                )}
              </div>
            ))}
            {loading && (
              <div className="flex gap-3 justify-start">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                  <Bot className="h-4 w-4 text-primary" />
                </div>
                <div className="bg-muted rounded-lg px-4 py-2">
                  <Loader2 className="h-4 w-4 animate-spin" />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </ScrollArea>
        <div className="border-t p-4 space-y-2">
          <FileUploadButton
            onFilesSelected={setSelectedFiles}
            maxFiles={5}
            maxSize={10 * 1024 * 1024}
            disabled={loading}
          />
          <div className="flex gap-2">
            <Textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={placeholder}
              className="min-h-[60px] resize-none"
              disabled={loading}
            />
            <Button
              onClick={handleSend}
              disabled={loading || (!input.trim() && selectedFiles.length === 0)}
              size="icon"
              className="h-[60px] w-[60px]"
            >
              {loading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

