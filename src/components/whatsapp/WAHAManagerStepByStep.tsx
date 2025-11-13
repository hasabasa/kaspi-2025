// components/whatsapp/WAHAManagerStepByStep.tsx
import { useState, useEffect } from 'react';
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
  Clock,
  ArrowRight,
  ArrowLeft,
  Phone,
  Key,
  Settings,
  BarChart3,
  Edit,
  Trash2,
  Power
} from 'lucide-react';

import { useWAHA } from '@/hooks/useWAHA';
import { TemplateForm } from './TemplateForm';
import { WhatsAppTemplate, TestMessage } from '@/services/wahaService';

interface ConnectionStep {
  id: number;
  title: string;
  description: string;
  icon: React.ReactNode;
  completed: boolean;
}

export default function WAHAManagerStepByStep() {
  const {
    session,
    sessionStatus,
    isLoading,
    error,
    templates,
    templatesLoading,
    templatesError,
    startSession,
    checkSessionStatus,
    deleteSession,
    createTemplate,
    updateTemplate,
    deleteTemplate,
    sendTestMessage,
    clearError
  } = useWAHA();

  const [currentStep, setCurrentStep] = useState(1);
  const [phoneNumber, setPhoneNumber] = useState('+7');
  const [connectionCode, setConnectionCode] = useState('');
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [showTemplateForm, setShowTemplateForm] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<WhatsAppTemplate | null>(null);
  const [testPhone, setTestPhone] = useState('');
  const [testMessage, setTestMessage] = useState('');
  const [testResult, setTestResult] = useState<{ success: boolean; error?: string } | null>(null);

  const [steps, setSteps] = useState<ConnectionStep[]>([
    {
      id: 1,
      title: 'Ввод номера телефона',
      description: 'Введите ваш номер телефона для подключения WhatsApp',
      icon: <Phone className="h-5 w-5" />,
      completed: false
    },
    {
      id: 2,
      title: 'Получение кода подключения',
      description: 'Получите код для связывания устройств',
      icon: <Key className="h-5 w-5" />,
      completed: false
    },
    {
      id: 3,
      title: 'Подтверждение в WhatsApp',
      description: 'Введите код в приложении WhatsApp',
      icon: <Smartphone className="h-5 w-5" />,
      completed: false
    },
    {
      id: 4,
      title: 'Настройка сообщений',
      description: 'Настройте автоматические сообщения и отчеты',
      icon: <Settings className="h-5 w-5" />,
      completed: false
    }
  ]);

  // Обновляем шаги на основе статуса сессии
  useEffect(() => {
    if (session) {
      setSteps(prev => prev.map(step => {
        if (step.id === 1) return { ...step, completed: true };
        if (step.id === 2 && session.status === 'connecting') return { ...step, completed: true };
        if (step.id === 3 && session.is_connected) return { ...step, completed: true };
        if (step.id === 4 && session.is_connected) return { ...step, completed: true };
        return step;
      }));

      if (session.is_connected) {
        setCurrentStep(4);
      } else if (session.status === 'connecting') {
        setCurrentStep(3);
      }
    }
  }, [session]);

  const handlePhoneSubmit = async () => {
    if (phoneNumber.length < 10) {
      alert('Пожалуйста, введите корректный номер телефона');
      return;
    }
    
    try {
      await startSession(phoneNumber);
      setSteps(prev => prev.map(step => 
        step.id === 1 ? { ...step, completed: true } : step
      ));
      setCurrentStep(2);
    } catch (err) {
      console.error('Ошибка создания сессии:', err);
    }
  };

  const handleGetConnectionCode = async () => {
    if (!session) return;
    
    try {
      // Получаем код из сессии (он уже должен быть получен при создании)
      if (session.expires_at) {
        setConnectionCode('XXXX-XXXX'); // Показываем маскированный код
        setSteps(prev => prev.map(step => 
          step.id === 2 ? { ...step, completed: true } : step
        ));
        setCurrentStep(3);
      }
    } catch (err) {
      console.error('Ошибка получения кода:', err);
    }
  };

  const handleCodeSubmit = () => {
    if (!connectionCode) {
      alert('Пожалуйста, получите код подключения');
      return;
    }
    
    setSteps(prev => prev.map(step => 
      step.id === 3 ? { ...step, completed: true } : step
    ));
    setCurrentStep(4);
  };

  const handleSendTest = async () => {
    if (!testPhone || !testMessage) return;
    
    const testData: TestMessage = {
      phone_number: testPhone,
      template_text: testMessage,
      sample_data: {
        user_name: 'Тестовый пользователь',
        order_num: '12345',
        product_name: 'Тестовый товар',
        item_qty: 1,
        shop_name: 'Мой магазин',
        delivery_type: 'самовывоз',
        order_date: new Date().toLocaleDateString('ru-RU'),
        total_amount: 1000,
        customer_phone: testPhone
      }
    };

    const result = await sendTestMessage(testData);
    setTestResult(result);
  };

  const handleCreateTemplate = async (template: { template_name: string; template_text: string; is_active?: boolean }) => {
    try {
      await createTemplate(template);
      setShowTemplateForm(false);
      setEditingTemplate(null);
    } catch (err) {
      console.error('Ошибка создания шаблона:', err);
    }
  };

  const handleUpdateTemplate = async (template: { template_name: string; template_text: string; is_active?: boolean }) => {
    if (!editingTemplate) return;
    
    try {
      await updateTemplate(editingTemplate.id, template);
      setShowTemplateForm(false);
      setEditingTemplate(null);
    } catch (err) {
      console.error('Ошибка обновления шаблона:', err);
    }
  };

  const handleDeleteTemplate = async (templateId: number) => {
    if (confirm('Вы уверены, что хотите удалить этот шаблон?')) {
      try {
        await deleteTemplate(templateId);
      } catch (err) {
        console.error('Ошибка удаления шаблона:', err);
      }
    }
  };

  const handleToggleTemplate = async (template: WhatsAppTemplate) => {
    try {
      await updateTemplate(template.id, { is_active: !template.is_active });
    } catch (err) {
      console.error('Ошибка обновления шаблона:', err);
    }
  };

  const handleDeleteSession = async () => {
    try {
      await deleteSession();
      setCurrentStep(1);
      setPhoneNumber('+7');
      setConnectionCode('');
      setSteps(prev => prev.map(step => ({ ...step, completed: false })));
      setShowDeleteConfirm(false);
    } catch (err) {
      console.error('Ошибка удаления сессии:', err);
    }
  };

  const getStatusIcon = () => {
    switch (sessionStatus) {
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
    switch (sessionStatus) {
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

  const getStatusText = () => {
    switch (sessionStatus) {
      case 'connected':
        return 'Подключено';
      case 'connecting':
        return 'Подключение...';
      case 'error':
        return 'Ошибка';
      default:
        return 'Отключено';
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Phone className="h-5 w-5" />
                Ввод номера телефона
              </CardTitle>
              <CardDescription>
                Введите ваш номер телефона для подключения WhatsApp
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}
              <div>
                <Label htmlFor="phoneNumber">Номер телефона</Label>
                <Input
                  id="phoneNumber"
                  value={phoneNumber}
                  onChange={(e) => setPhoneNumber(e.target.value)}
                  placeholder="+7 (___) ___-__-__"
                  className="text-lg"
                  disabled={isLoading}
                />
                <p className="text-xs text-muted-foreground mt-1">
                  Пример: +7 (701) 123-45-67
                </p>
              </div>
              <Button onClick={handlePhoneSubmit} className="w-full" disabled={isLoading}>
                <ArrowRight className="h-4 w-4 mr-2" />
                {isLoading ? 'Подключение...' : 'Продолжить'}
              </Button>
            </CardContent>
          </Card>
        );

      case 2:
        return (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Key className="h-5 w-5" />
                Получение кода подключения
              </CardTitle>
              <CardDescription>
                Получите код для связывания устройств в WhatsApp
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Alert>
                <AlertDescription>
                  Нажмите кнопку ниже, чтобы получить код подключения для вашего номера {phoneNumber}
                </AlertDescription>
              </Alert>
              <div className="space-y-2">
                <Button onClick={handleGetConnectionCode} className="w-full" disabled={isLoading}>
                  {isLoading ? (
                    <>
                      <Clock className="h-4 w-4 mr-2" />
                      Получение кода...
                    </>
                  ) : (
                    <>
                      <Key className="h-4 w-4 mr-2" />
                      Получить код подключения
                    </>
                  )}
                </Button>
                <Button 
                  variant="outline" 
                  onClick={() => setShowDeleteConfirm(true)}
                  className="w-full"
                >
                  <XCircle className="h-4 w-4 mr-2" />
                  Начать заново
                </Button>
              </div>
            </CardContent>
          </Card>
        );

      case 3:
        return (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Smartphone className="h-5 w-5" />
                Подтверждение в WhatsApp
              </CardTitle>
              <CardDescription>
                Введите полученный код в приложении WhatsApp
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Alert>
                <AlertDescription>
                  <strong>Код подключения:</strong> {connectionCode}
                </AlertDescription>
              </Alert>
              
              <div className="bg-blue-50 p-4 rounded-lg">
                <h4 className="font-semibold mb-2">Инструкция:</h4>
                <ol className="list-decimal list-inside space-y-1 text-sm">
                  <li>Откройте приложение WhatsApp на вашем телефоне</li>
                  <li>Перейдите в Настройки → Связанные устройства</li>
                  <li>Нажмите "Связать устройство"</li>
                  <li>Введите код: <strong>{connectionCode}</strong></li>
                  <li>Подтвердите подключение</li>
                </ol>
              </div>

              <div className="space-y-2">
                <Button onClick={handleCodeSubmit} className="w-full">
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Я подтвердил подключение
                </Button>
                <Button 
                  variant="outline" 
                  onClick={() => setShowDeleteConfirm(true)}
                  className="w-full"
                >
                  <XCircle className="h-4 w-4 mr-2" />
                  Начать заново
                </Button>
              </div>
            </CardContent>
          </Card>
        );

      case 4:
        return (
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="flex items-center gap-2">
                      <CheckCircle className="h-5 w-5 text-green-500" />
                      WhatsApp подключен успешно!
                    </CardTitle>
                    <CardDescription>
                      Теперь вы можете настроить автоматические сообщения и отчеты
                    </CardDescription>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge className={getStatusColor()}>
                      {getStatusIcon()}
                      <span className="ml-1">{getStatusText()}</span>
                    </Badge>
                    <Button 
                      variant="destructive" 
                      size="sm"
                      onClick={() => setShowDeleteConfirm(true)}
                    >
                      <XCircle className="h-4 w-4 mr-2" />
                      Удалить сессию
                    </Button>
                  </div>
                </div>
              </CardHeader>
            </Card>

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
                    {templatesError && (
                      <Alert variant="destructive">
                        <AlertDescription>{templatesError}</AlertDescription>
                      </Alert>
                    )}
                    <div className="space-y-4">
                      {templatesLoading ? (
                        <div className="space-y-4">
                          {[...Array(2)].map((_, i) => (
                            <Card key={i} className="p-4">
                              <div className="h-20 bg-gray-200 rounded animate-pulse" />
                            </Card>
                          ))}
                        </div>
                      ) : templates.length > 0 ? (
                        templates.map((template) => (
                          <Card key={template.id} className="p-4">
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-2">
                                  <h3 className="font-semibold">{template.template_name}</h3>
                                  <Badge variant={template.is_active ? "default" : "secondary"}>
                                    {template.is_active ? "Активен" : "Неактивен"}
                                  </Badge>
                                </div>
                                <p className="text-sm text-muted-foreground mb-2 whitespace-pre-line">
                                  {template.template_text}
                                </p>
                                <div className="flex items-center gap-2">
                                  <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => handleToggleTemplate(template)}
                                  >
                                    <Power className="h-3 w-3 mr-1" />
                                    {template.is_active ? 'Деактивировать' : 'Активировать'}
                                  </Button>
                                  <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => {
                                      setEditingTemplate(template);
                                      setShowTemplateForm(true);
                                    }}
                                  >
                                    <Edit className="h-3 w-3 mr-1" />
                                    Редактировать
                                  </Button>
                                  <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => handleDeleteTemplate(template.id)}
                                  >
                                    <Trash2 className="h-3 w-3 mr-1" />
                                    Удалить
                                  </Button>
                                </div>
                              </div>
                            </div>
                          </Card>
                        ))
                      ) : (
                        <div className="text-center py-8 text-gray-500">
                          <p>Шаблоны не найдены</p>
                          <p className="text-sm">Создайте первый шаблон для автоматических уведомлений</p>
                        </div>
                      )}
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
                    {testResult && (
                      <Alert variant={testResult.success ? "default" : "destructive"}>
                        <AlertDescription>
                          {testResult.success 
                            ? 'Тестовое сообщение отправлено успешно!' 
                            : `Ошибка: ${testResult.error}`
                          }
                        </AlertDescription>
                      </Alert>
                    )}
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
                    <CardTitle className="flex items-center gap-2">
                      <BarChart3 className="h-5 w-5" />
                      Статистика
                    </CardTitle>
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
          </div>
        );

      default:
        return null;
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
          Пошаговое подключение WhatsApp и настройка автоматических сообщений
        </p>
      </div>

      {/* Прогресс шагов */}
      <Card>
        <CardHeader>
          <CardTitle>Процесс подключения</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            {steps.map((step, index) => (
              <div key={step.id} className="flex items-center">
                <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${
                  step.completed 
                    ? 'bg-green-500 border-green-500 text-white' 
                    : currentStep === step.id 
                      ? 'bg-blue-500 border-blue-500 text-white' 
                      : 'bg-gray-100 border-gray-300 text-gray-500'
                }`}>
                  {step.completed ? (
                    <CheckCircle className="h-5 w-5" />
                  ) : (
                    step.icon
                  )}
                </div>
                <div className="ml-3">
                  <p className={`text-sm font-medium ${
                    step.completed || currentStep === step.id ? 'text-gray-900' : 'text-gray-500'
                  }`}>
                    {step.title}
                  </p>
                  <p className="text-xs text-gray-500">{step.description}</p>
                </div>
                {index < steps.length - 1 && (
                  <ArrowRight className="h-4 w-4 text-gray-400 mx-4" />
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Контент текущего шага */}
      {renderStepContent()}

      {/* Навигация */}
      {currentStep > 1 && currentStep < 4 && (
        <div className="flex justify-between">
          <Button 
            variant="outline" 
            onClick={() => setCurrentStep(currentStep - 1)}
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Назад
          </Button>
          <div className="text-sm text-muted-foreground">
            Шаг {currentStep} из {steps.length}
          </div>
        </div>
      )}

      {/* Модальное окно для создания/редактирования шаблона */}
      {showTemplateForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="w-full max-w-6xl max-h-[90vh] overflow-y-auto">
            <TemplateForm
              template={editingTemplate || undefined}
              onSave={editingTemplate ? handleUpdateTemplate : handleCreateTemplate}
              onCancel={() => {
                setShowTemplateForm(false);
                setEditingTemplate(null);
              }}
              loading={templatesLoading}
            />
          </div>
        </div>
      )}

      {/* Модальное окно подтверждения удаления сессии */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-red-600">
                <XCircle className="h-5 w-5" />
                Удаление сессии WhatsApp
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Alert variant="destructive">
                <AlertDescription>
                  <strong>Внимание!</strong> Вы собираетесь удалить текущую сессию WhatsApp.
                </AlertDescription>
              </Alert>
              
              <div className="space-y-2">
                <p className="text-sm text-muted-foreground">
                  Это действие приведет к:
                </p>
                <ul className="list-disc list-inside text-sm text-muted-foreground space-y-1">
                  <li>Отключению текущего номера телефона</li>
                  <li>Потере доступа к отправке сообщений</li>
                  <li>Необходимости повторного подключения</li>
                </ul>
              </div>

              <div className="bg-blue-50 p-3 rounded-lg">
                <p className="text-sm text-blue-800">
                  <strong>Текущий номер:</strong> {phoneNumber}
                </p>
                <p className="text-xs text-blue-600 mt-1">
                  После удаления вы сможете подключить другой номер телефона
                </p>
              </div>

              <div className="flex gap-2">
                <Button 
                  variant="destructive" 
                  onClick={handleDeleteSession}
                  className="flex-1"
                >
                  <XCircle className="h-4 w-4 mr-2" />
                  Удалить сессию
                </Button>
                <Button 
                  variant="outline"
                  onClick={() => setShowDeleteConfirm(false)}
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
