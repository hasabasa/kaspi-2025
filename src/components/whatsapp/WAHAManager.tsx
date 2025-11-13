// components/whatsapp/WAHAManager.tsx
import { useState } from 'react';
import { useWAHA } from '@/hooks/useWAHA';
import { useMobileOptimizedSimple as useMobileOptimized } from "@/hooks/useMobileOptimizedSimple";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { 
  Smartphone, 
  QrCode, 
  MessageSquare, 
  Settings, 
  Send, 
  Plus, 
  Edit, 
  Trash2,
  CheckCircle,
  XCircle,
  Clock,
  BarChart3
} from 'lucide-react';

interface TemplateFormData {
  name: string;
  content: string;
  variables: string[];
}

export default function WAHAManager() {
  const mobile = useMobileOptimized();
  const {
    config,
    setConfig,
    status,
    templates,
    stats,
    isLoading,
    createSession,
    getQRCode,
    sendTestMessage,
    createTemplate,
    updateTemplate,
    deleteTemplate
  } = useWAHA();

  const [testPhone, setTestPhone] = useState('');
  const [testMessage, setTestMessage] = useState('');
  const [showTemplateForm, setShowTemplateForm] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<string | null>(null);
  const [templateForm, setTemplateForm] = useState<TemplateFormData>({
    name: '',
    content: '',
    variables: []
  });

  const handleCreateSession = async () => {
    await createSession();
    setTimeout(() => {
      getQRCode();
    }, 2000);
  };

  const handleSendTestMessage = async () => {
    if (!testPhone || !testMessage) return;
    
    try {
      await sendTestMessage(testPhone, testMessage);
      alert('Тестовое сообщение отправлено!');
    } catch (error) {
      alert('Ошибка отправки сообщения: ' + error);
    }
  };

  const handleCreateTemplate = async () => {
    if (!templateForm.name || !templateForm.content) return;
    
    try {
      await createTemplate({
        ...templateForm,
        isActive: true
      });
      setShowTemplateForm(false);
      setTemplateForm({ name: '', content: '', variables: [] });
    } catch (error) {
      alert('Ошибка создания шаблона: ' + error);
    }
  };

  const handleUpdateTemplate = async () => {
    if (!editingTemplate || !templateForm.name || !templateForm.content) return;
    
    try {
      await updateTemplate(editingTemplate, templateForm);
      setEditingTemplate(null);
      setTemplateForm({ name: '', content: '', variables: [] });
    } catch (error) {
      alert('Ошибка обновления шаблона: ' + error);
    }
  };

  const handleDeleteTemplate = async (id: string) => {
    if (confirm('Вы уверены, что хотите удалить этот шаблон?')) {
      try {
        await deleteTemplate(id);
      } catch (error) {
        alert('Ошибка удаления шаблона: ' + error);
      }
    }
  };

  const extractVariables = (content: string) => {
    const matches = content.match(/\{([^}]+)\}/g);
    return matches ? matches.map(match => match.slice(1, -1)) : [];
  };

  const getStatusIcon = () => {
    switch (status.status) {
      case 'connected':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'connecting':
        return <Clock className="h-5 w-5 text-yellow-500" />;
      case 'error':
        return <XCircle className="h-5 w-5 text-red-500" />;
      default:
        return <XCircle className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusColor = () => {
    switch (status.status) {
      case 'connected':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'connecting':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'error':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <div className={cn(
      "container mx-auto p-4 space-y-6",
      mobile.isMobile ? "px-2" : "px-6"
    )}>
      {/* Заголовок */}
      <div className="text-center">
        <h1 className={cn(
          "font-bold mb-2",
          mobile.isMobile ? mobile.getTextSize('xl') : "text-3xl"
        )}>
          WhatsApp Автоматизация
        </h1>
        <p className={cn(
          "text-muted-foreground",
          mobile.getTextSize('sm')
        )}>
          Подключение WhatsApp и настройка автоматических сообщений
        </p>
      </div>

      {/* Статус подключения */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Smartphone className="h-5 w-5" />
            Статус подключения
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {getStatusIcon()}
              <div>
                <p className="font-medium">{status.message}</p>
                {status.sessionInfo && (
                  <p className="text-sm text-muted-foreground">
                    {status.sessionInfo.phone && `Телефон: ${status.sessionInfo.phone}`}
                  </p>
                )}
              </div>
            </div>
            <Badge className={cn("px-3 py-1", getStatusColor())}>
              {status.status === 'connected' ? 'Подключено' : 
               status.status === 'connecting' ? 'Подключение...' : 
               status.status === 'error' ? 'Ошибка' : 'Отключено'}
            </Badge>
          </div>

          {status.status === 'disconnected' && (
            <div className="mt-4">
              <Button 
                onClick={handleCreateSession} 
                disabled={isLoading}
                className="w-full"
              >
                {isLoading ? 'Создание сессии...' : 'Подключить WhatsApp'}
              </Button>
            </div>
          )}

          {status.status === 'connecting' && (
            <div className="mt-4">
              <Button 
                onClick={getQRCode} 
                disabled={isLoading}
                variant="outline"
                className="w-full"
              >
                <QrCode className="h-4 w-4 mr-2" />
                Получить QR-код
              </Button>
            </div>
          )}

          {status.qrCode && (
            <div className="mt-6 text-center">
              <img
                src={status.qrCode}
                alt="QR-код WhatsApp"
                className="mx-auto border rounded-lg"
                style={{ 
                  width: mobile.isSmallPhone ? '200px' : '250px', 
                  height: mobile.isSmallPhone ? '200px' : '250px' 
                }}
              />
              <p className={cn(
                "text-muted-foreground mt-2",
                mobile.getTextSize('xs')
              )}>
                Откройте WhatsApp → Настройки → Связанные устройства → Отсканировать QR-код
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Основные функции */}
      <Tabs defaultValue="templates" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="templates">Шаблоны</TabsTrigger>
          <TabsTrigger value="test">Тестирование</TabsTrigger>
          <TabsTrigger value="stats">Статистика</TabsTrigger>
        </TabsList>

        {/* Шаблоны сообщений */}
        <TabsContent value="templates" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Шаблоны сообщений</CardTitle>
                  <CardDescription>
                    Создайте и настройте автоматические сообщения для клиентов
                  </CardDescription>
                </div>
                <Button 
                  onClick={() => setShowTemplateForm(true)}
                  disabled={status.status !== 'connected'}
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Новый шаблон
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {templates.length === 0 ? (
                <Alert>
                  <AlertDescription>
                    Шаблоны не найдены. Создайте первый шаблон для автоматических сообщений.
                  </AlertDescription>
                </Alert>
              ) : (
                <div className="space-y-4">
                  {templates.map((template) => (
                    <Card key={template.id} className="p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <h3 className="font-semibold">{template.name}</h3>
                            <Badge variant={template.isActive ? "default" : "secondary"}>
                              {template.isActive ? "Активен" : "Неактивен"}
                            </Badge>
                          </div>
                          <p className="text-sm text-muted-foreground mb-2">
                            {template.content}
                          </p>
                          {template.variables.length > 0 && (
                            <div className="flex flex-wrap gap-1">
                              {template.variables.map((variable) => (
                                <Badge key={variable} variant="outline" className="text-xs">
                                  {`{${variable}}`}
                                </Badge>
                              ))}
                            </div>
                          )}
                        </div>
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => {
                              setEditingTemplate(template.id);
                              setTemplateForm({
                                name: template.name,
                                content: template.content,
                                variables: template.variables
                              });
                            }}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleDeleteTemplate(template.id)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Тестирование */}
        <TabsContent value="test" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Send className="h-5 w-5" />
                Тестирование сообщений
              </CardTitle>
              <CardDescription>
                Отправьте тестовое сообщение для проверки работы WhatsApp
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="testPhone">Номер телефона</Label>
                <Input
                  id="testPhone"
                  placeholder="77001234567"
                  value={testPhone}
                  onChange={(e) => setTestPhone(e.target.value)}
                />
              </div>
              <div>
                <Label htmlFor="testMessage">Сообщение</Label>
                <Textarea
                  id="testMessage"
                  placeholder="Введите текст сообщения..."
                  value={testMessage}
                  onChange={(e) => setTestMessage(e.target.value)}
                  rows={4}
                />
              </div>
              <Button 
                onClick={handleSendTestMessage}
                disabled={!testPhone || !testMessage || status.status !== 'connected' || isLoading}
                className="w-full"
              >
                <Send className="h-4 w-4 mr-2" />
                Отправить тестовое сообщение
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Статистика */}
        <TabsContent value="stats" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                Статистика
              </CardTitle>
            </CardHeader>
            <CardContent>
              {stats ? (
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-green-600">{stats.messagesSent}</p>
                    <p className="text-sm text-muted-foreground">Отправлено</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-blue-600">{stats.messagesReceived}</p>
                    <p className="text-sm text-muted-foreground">Получено</p>
                  </div>
                </div>
              ) : (
                <Alert>
                  <AlertDescription>
                    Статистика недоступна. Подключите WhatsApp для просмотра статистики.
                  </AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Модальное окно для создания/редактирования шаблона */}
      {(showTemplateForm || editingTemplate) && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle>
                {editingTemplate ? 'Редактировать шаблон' : 'Новый шаблон'}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="templateName">Название шаблона</Label>
                <Input
                  id="templateName"
                  placeholder="Уведомление о заказе"
                  value={templateForm.name}
                  onChange={(e) => setTemplateForm(prev => ({ ...prev, name: e.target.value }))}
                />
              </div>
              <div>
                <Label htmlFor="templateContent">Содержание сообщения</Label>
                <Textarea
                  id="templateContent"
                  placeholder="Здравствуйте, {user_name}. Ваш заказ {order_num} готов к самовывозу."
                  value={templateForm.content}
                  onChange={(e) => {
                    const content = e.target.value;
                    const variables = extractVariables(content);
                    setTemplateForm(prev => ({ ...prev, content, variables }));
                  }}
                  rows={6}
                />
                <p className="text-xs text-muted-foreground mt-1">
                  Используйте переменные в фигурных скобках: {`{user_name}`}, {`{order_num}`}, {`{product_name}`}
                </p>
              </div>
              {templateForm.variables.length > 0 && (
                <div>
                  <Label>Переменные в шаблоне:</Label>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {templateForm.variables.map((variable) => (
                      <Badge key={variable} variant="outline" className="text-xs">
                        {`{${variable}}`}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
              <div className="flex gap-2">
                <Button 
                  onClick={editingTemplate ? handleUpdateTemplate : handleCreateTemplate}
                  disabled={!templateForm.name || !templateForm.content}
                  className="flex-1"
                >
                  {editingTemplate ? 'Обновить' : 'Создать'}
                </Button>
                <Button 
                  variant="outline"
                  onClick={() => {
                    setShowTemplateForm(false);
                    setEditingTemplate(null);
                    setTemplateForm({ name: '', content: '', variables: [] });
                  }}
                >
                  Отмена
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
