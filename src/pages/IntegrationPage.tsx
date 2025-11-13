
import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Store, Mail, Phone } from "lucide-react";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import { API_URL, API_BASE_PATH } from "@/config";

const API_BASE_URL = `${API_URL}${API_BASE_PATH}`;

const IntegrationPage = () => {
  // const mobile = useMobileOptimized();
  
  // Email метод
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isEmailConnecting, setIsEmailConnecting] = useState(false);
  
  // Phone метод
  const [phone, setPhone] = useState("");
  const [smsCode, setSmsCode] = useState("");
  const [isPhoneConnecting, setIsPhoneConnecting] = useState(false);
  const [showSmsStep, setShowSmsStep] = useState(false);
  
  const [connectedStores, setConnectedStores] = useState<any[]>([]);
  const [sessionId, setSessionId] = useState<string>("");

  // Загрузка существующих магазинов
  useEffect(() => {
    loadConnectedStores();
  }, []);

  const loadConnectedStores = async () => {
    try {
      // Используем реальный user_id вместо demo_user
      const userId = "real_user_playwright"; // Или получать из контекста пользователя
      const response = await fetch(`${API_BASE_URL}/kaspi/stores?user_id=${userId}`);
      if (response.ok) {
        const stores = await response.json();
        console.log("Загруженные магазины:", stores);
        setConnectedStores(stores.map((store: any) => ({
          ...store,
          method: "email",
          status: store.is_active ? "active" : "inactive",
          connectedAt: store.created_at
        })));
      }
    } catch (error) {
      console.log("Ошибка загрузки магазинов:", error);
    }
  };

  // Подключение через Email + Пароль
  const handleEmailConnect = async () => {
    if (!email || !password) {
      toast.error("Заполните email и пароль");
      return;
    }

    setIsEmailConnecting(true);
    try {
      const response = await fetch(`${API_BASE_URL}/kaspi/auth`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: "real_user_playwright", // Используем реальный user_id
          email: email,
          password: password,
          auth_method: "playwright" // Используем правильный метод авторизации
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Ошибка подключения к Kaspi');
      }

      const result = await response.json();
      console.log("Результат подключения:", result);
      
      if (result.success) {
        // Обновляем список магазинов после успешного подключения
        await loadConnectedStores();
        
        setEmail("");
        setPassword("");
        toast.success("Магазин успешно подключен!");
      } else {
        throw new Error(result.error || "Неудачное подключение");
      }
    } catch (error: any) {
      console.error("Ошибка подключения:", error);
      toast.error(error.message || "Ошибка подключения магазина");
    } finally {
      setIsEmailConnecting(false);
    }
  };

  // Получение SMS кода для телефона
  const handleGetSmsCode = async () => {
    if (!phone) {
      toast.error("Введите номер телефона");
      return;
    }

    // Проверка формата номера телефона (должен начинаться с 7)
    if (!phone.match(/^7\d{10}$/)) {
      toast.error("Номер телефона должен быть в формате 7XXXXXXXXXX (без + и 8)");
      return;
    }

    setIsPhoneConnecting(true);
    try {
      // Имитация отправки SMS
      await new Promise(resolve => setTimeout(resolve, 1000));
      setShowSmsStep(true);
      toast.success("SMS код отправлен на номер " + phone);
    } catch (error) {
      toast.error("Ошибка при отправке SMS");
    } finally {
      setIsPhoneConnecting(false);
    }
  };

  // Подключение через SMS
  const handlePhoneConnect = async () => {
    if (!smsCode) {
      toast.error("Введите SMS код");
      return;
    }

    setIsPhoneConnecting(true);
    try {
      // Имитация подключения магазина
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      const newStore = {
        id: Date.now().toString(),
        name: "Мой магазин Kaspi (SMS)",
        phone: phone,
        method: "phone",
        status: "active",
        connectedAt: new Date().toISOString()
      };
      
      setConnectedStores([...connectedStores, newStore]);
      setShowSmsStep(false);
      setPhone("");
      setSmsCode("");
      toast.success("Магазин успешно подключен через SMS!");
    } catch (error) {
      toast.error("Ошибка подключения магазина");
    } finally {
      setIsPhoneConnecting(false);
    }
  };

  return (
    <div className="container mx-auto p-4 md:p-6 space-y-6">
      {/* Заголовок */}
      <div className="text-center">
        <div className="flex flex-col items-center gap-3">
          <Store className="h-8 w-8 text-gray-600 dark:text-gray-400" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              Подключение магазина
            </h1>
            <p className="text-base text-gray-600 dark:text-gray-400">
              Подключите ваш магазин Kaspi.kz для работы с платформой
            </p>
          </div>
        </div>
      </div>

      {/* Список подключенных магазинов */}
      {connectedStores.length > 0 && (
        <div className="space-y-4">
          <h2 className="font-medium text-gray-900 dark:text-white">Подключенные магазины</h2>
          {connectedStores.map((store) => (
            <Card key={store.id} className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Store className="h-5 w-5 text-gray-600 dark:text-gray-400" />
                  <div>
                    <h3 className="font-medium text-gray-900 dark:text-white">{store.name}</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {store.email || store.phone} • {store.method === 'email' ? 'Email' : 'SMS'}
                    </p>
                  </div>
                </div>
                <div className="text-sm text-green-600 dark:text-green-400">Активен</div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Способы подключения */}
      <Card>
        <CardHeader>
          <CardTitle>
            {connectedStores.length > 0 ? "Подключить новый магазин" : "Подключение магазина"}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="email" className="w-full">
            <TabsList className="grid w-full grid-cols-2 h-auto">
              <TabsTrigger 
                value="email" 
                className="flex items-center gap-2 px-3 py-2 text-xs sm:text-sm md:text-base"
              >
                <Mail className="h-4 w-4 flex-shrink-0" />
                <span className="hidden sm:inline truncate">
                  Email + Пароль
                </span>
                <span className="sm:hidden truncate">
                  Email
                </span>
              </TabsTrigger>
              <TabsTrigger 
                value="phone" 
                className="flex items-center gap-2 px-3 py-2 text-xs sm:text-sm md:text-base"
              >
                <Phone className="h-4 w-4 flex-shrink-0" />
                <span className="hidden sm:inline truncate">
                  Номер телефона
                </span>
                <span className="sm:hidden truncate">
                  Телефон
                </span>
              </TabsTrigger>
            </TabsList>

            {/* Email способ */}
            <TabsContent value="email" className="space-y-4 mt-6">
              <div>
                <Label htmlFor="email" className="text-sm font-medium mb-2 block">
                  Email от Kaspi.kz
                </Label>
                <Input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Введите email"
                />
              </div>

              <div>
                <Label htmlFor="password" className="text-sm font-medium mb-2 block">
                  Пароль от Kaspi.kz
                </Label>
                <Input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Введите пароль"
                />
              </div>

              <Button 
                onClick={handleEmailConnect} 
                disabled={isEmailConnecting || !email || !password}
                className="w-full"
              >
                {isEmailConnecting ? "Подключение..." : "Подключить магазин"}
              </Button>
            </TabsContent>

            {/* Phone способ */}
            <TabsContent value="phone" className="space-y-4 mt-6">
              {!showSmsStep ? (
                <>
                  <div>
                    <Label htmlFor="phone" className="text-sm font-medium mb-2 block">
                      Номер телефона (формат: 7XXXXXXXXXX)
                    </Label>
                    <Input
                      id="phone"
                      type="tel"
                      value={phone}
                      onChange={(e) => setPhone(e.target.value.replace(/[^\d]/g, ''))}
                      placeholder="7XXXXXXXXXX"
                      maxLength={11}
                    />
                    <p className="text-xs text-muted-foreground mt-1">
                      Введите номер без + и 8, начиная с 7
                    </p>
                  </div>

                  <Button 
                    onClick={handleGetSmsCode} 
                    disabled={isPhoneConnecting || !phone}
                    className="w-full"
                  >
                    {isPhoneConnecting ? "Отправка SMS..." : "Получить код"}
                  </Button>
                </>
              ) : (
                <>
                  <div>
                    <Label htmlFor="smsCode" className="text-sm font-medium mb-2 block">
                      SMS код подтверждения
                    </Label>
                    <Input
                      id="smsCode"
                      type="text"
                      value={smsCode}
                      onChange={(e) => setSmsCode(e.target.value.replace(/[^\d]/g, ''))}
                      placeholder="Введите код из SMS"
                      maxLength={6}
                    />
                    <p className="text-xs text-muted-foreground mt-1">
                      Код отправлен на номер {phone}
                    </p>
                  </div>

                  <div className="flex gap-3">
                    <Button 
                      variant="outline" 
                      onClick={() => setShowSmsStep(false)}
                      className="flex-1"
                    >
                      Назад
                    </Button>
                    <Button 
                      onClick={handlePhoneConnect} 
                      disabled={isPhoneConnecting || !smsCode}
                      className="flex-1"
                    >
                      {isPhoneConnecting ? "Подключение..." : "Подключить магазин"}
                    </Button>
                  </div>
                </>
              )}
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
};

export default IntegrationPage;
