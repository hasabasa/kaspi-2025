// components/whatsapp/WAHAManagerSimple.tsx
import { useState } from 'react';
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
  Send, 
  Plus, 
  CheckCircle,
  XCircle,
  Clock
} from 'lucide-react';

interface WhatsAppTemplate {
  id: string;
  name: string;
  content: string;
  variables: string[];
  isActive: boolean;
}

export default function WAHAManagerSimple() {
  const [status, setStatus] = useState({
    status: 'disconnected' as 'disconnected' | 'connecting' | 'connected' | 'error',
    message: 'WhatsApp не подключен',
    qrCode: null as string | null
  });
  
  const [templates, setTemplates] = useState<WhatsAppTemplate[]>([
    {
      id: '1',
      name: 'Уведомление о заказе',
      content: 'Здравствуйте, {user_name}!\n\nВаш заказ №{order_num} "{product_name}", количество: {item_qty} шт готов к самовывозу.\n\n* В ближайшее время мы свяжемся с вами для уточнения деталей заказа.\n* Спасибо за Ваш выбор! Если у Вас есть вопросы, обращайтесь в любое время.\n\nС уважением,\n{shop_name}',
      variables: ['user_name', 'order_num', 'product_name', 'item_qty', 'shop_name'],
      isActive: true
    },
    {
      id: '2',
      name: 'Уведомление о доставке',
      content: 'Здравствуйте, {user_name}!\n\nВаш заказ №{order_num} отправлен и будет доставлен в течение 1-2 рабочих дней.\n\nТрек-номер: {tracking_number}\n\nСпасибо за покупку!\n\nС уважением,\n{shop_name}',
      variables: ['user_name', 'order_num', 'tracking_number', 'shop_name'],
      isActive: true
    }
  ]);
  
  const [testPhone, setTestPhone] = useState('');
  const [testMessage, setTestMessage] = useState('');
  const [showTemplateForm, setShowTemplateForm] = useState(false);
  const [templateForm, setTemplateForm] = useState({
    name: '',
    content: '',
    variables: [] as string[]
  });

  const handleConnect = () => {
    setStatus({
      status: 'connecting',
      message: 'Подключение к WhatsApp...',
      qrCode: null
    });
    
    // Симуляция подключения
    setTimeout(() => {
      setStatus({
        status: 'connected',
        message: 'WhatsApp подключен успешно',
        qrCode: null
      });
    }, 2000);
  };

  const handleGetQR = () => {
    setStatus(prev => ({
      ...prev,
      qrCode: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjUwIiBoZWlnaHQ9IjI1MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMjUwIiBoZWlnaHQ9IjI1MCIgZmlsbD0iI2ZmZiIvPjx0ZXh0IHg9IjEyNSIgeT0iMTI1IiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTQiIGZpbGw9IiMwMDAiIHRleHQtYW5jaG9yPSJtaWRkbGUiPk1vY2sgUVIgQ29kZTwvdGV4dD48L3N2Zz4='
    }));
  };

  const handleSendTest = () => {
    if (!testPhone || !testMessage) return;
    alert(`Тестовое сообщение отправлено на номер ${testPhone}:\n\n${testMessage}`);
  };

  const handleCreateTemplate = () => {
    if (!templateForm.name || !templateForm.content) return;
    
    const variables = templateForm.content.match(/\{([^}]+)\}/g)?.map(v => v.slice(1, -1)) || [];
    
    const newTemplate: WhatsAppTemplate = {
      id: Date.now().toString(),
      name: templateForm.name,
      content: templateForm.content,
      variables,
      isActive: true
    };
    
    setTemplates(prev => [...prev, newTemplate]);
    setShowTemplateForm(false);
    setTemplateForm({ name: '', content: '', variables: [] });
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
    <div className="container mx-auto p-4 space-y-6">
      {/* Заголовок */}
      <div className="text-center">
        <h1 className="text-3xl font-bold mb-2">
          WhatsApp Автоматизация
        </h1>
        <p className="text-muted-foreground">
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
              </div>
            </div>
            <Badge className={`px-3 py-1 ${getStatusColor()}`}>
              {status.status === 'connected' ? 'Подключено' : 
               status.status === 'connecting' ? 'Подключение...' : 
               status.status === 'error' ? 'Ошибка' : 'Отключено'}
            </Badge>
          </div>

          {status.status === 'disconnected' && (
            <div className="mt-4">
              <Button onClick={handleConnect} className="w-full">
                Подключить WhatsApp
              </Button>
            </div>
          )}

          {status.status === 'connecting' && (
            <div className="mt-4">
              <Button onClick={handleGetQR} variant="outline" className="w-full">
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
                className="mx-auto border rounded-lg w-64 h-64"
              />
              <p className="text-muted-foreground mt-2 text-sm">
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
                <Button onClick={() => setShowTemplateForm(true)}>
                  <Plus className="h-4 w-4 mr-2" />
                  Новый шаблон
                </Button>
              </div>
            </CardHeader>
            <CardContent>
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
                        <p className="text-sm text-muted-foreground mb-2 whitespace-pre-line">
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
                    </div>
                  </Card>
                ))}
              </div>
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
                onClick={handleSendTest}
                disabled={!testPhone || !testMessage}
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
              <CardTitle>Статистика</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center">
                  <p className="text-2xl font-bold text-green-600">0</p>
                  <p className="text-sm text-muted-foreground">Отправлено</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-blue-600">0</p>
                  <p className="text-sm text-muted-foreground">Получено</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Модальное окно для создания шаблона */}
      {showTemplateForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle>Новый шаблон</CardTitle>
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
                  onChange={(e) => setTemplateForm(prev => ({ ...prev, content: e.target.value }))}
                  rows={6}
                />
                <p className="text-xs text-muted-foreground mt-1">
                  Используйте переменные в фигурных скобках: {`{user_name}`}, {`{order_num}`}, {`{product_name}`}
                </p>
              </div>
              <div className="flex gap-2">
                <Button onClick={handleCreateTemplate} className="flex-1">
                  Создать
                </Button>
                <Button 
                  variant="outline"
                  onClick={() => {
                    setShowTemplateForm(false);
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
