
import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "sonner";
import { Lock, Eye, EyeOff, AlertCircle } from "lucide-react";
import { supabase } from "@/integrations/supabase/client";

const ResetPasswordPage = () => {
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isValidToken, setIsValidToken] = useState(false);
  const [isCheckingToken, setIsCheckingToken] = useState(true);
  const [debugInfo, setDebugInfo] = useState<string>('');
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  useEffect(() => {
    const checkTokenAndSetSession = async () => {
      try {
        // Получаем все параметры из URL для диагностики
        const allParams = Object.fromEntries(searchParams.entries());
        console.log('🔍 Reset password URL analysis:', {
          currentURL: window.location.href,
          allParams,
          hasHash: !!window.location.hash,
          hash: window.location.hash
        });

        // Проверяем токены в URL parameters
        const accessToken = searchParams.get('access_token');
        const refreshToken = searchParams.get('refresh_token');
        const type = searchParams.get('type');
        const error = searchParams.get('error');
        const errorDescription = searchParams.get('error_description');

        // Также проверяем токены в hash (если Supabase использует hash-based routing)
        const hash = window.location.hash.substring(1);
        const hashParams = new URLSearchParams(hash);
        const hashAccessToken = hashParams.get('access_token');
        const hashRefreshToken = hashParams.get('refresh_token');
        const hashType = hashParams.get('type');
        const hashError = hashParams.get('error');

        console.log('🔍 Token analysis:', {
          fromParams: { accessToken: !!accessToken, refreshToken: !!refreshToken, type, error, errorDescription },
          fromHash: { accessToken: !!hashAccessToken, refreshToken: !!hashRefreshToken, type: hashType, error: hashError }
        });

        // Если есть ошибка в параметрах
        if (error || hashError) {
          const errorMsg = errorDescription || hashError || 'Unknown error';
          console.error('❌ Error in URL:', errorMsg);
          setDebugInfo(`Error in URL: ${errorMsg}`);
          toast.error(`Ошибка в ссылке сброса пароля: ${errorMsg}`);
          setTimeout(() => navigate('/auth'), 3000);
          return;
        }

        // Используем токены из hash, если они есть, иначе из params
        const finalAccessToken = hashAccessToken || accessToken;
        const finalRefreshToken = hashRefreshToken || refreshToken;
        const finalType = hashType || type;

        console.log('🔍 Final tokens:', {
          hasAccessToken: !!finalAccessToken,
          hasRefreshToken: !!finalRefreshToken,
          type: finalType
        });

        if (!finalAccessToken || !finalRefreshToken) {
          console.error('❌ Missing required tokens');
          setDebugInfo('Missing access_token or refresh_token in URL');
          toast.error('Недействительная ссылка для сброса пароля. Отсутствуют необходимые токены.');
          setTimeout(() => navigate('/auth'), 3000);
          return;
        }

        if (finalType !== 'recovery') {
          console.error('❌ Invalid token type:', finalType);
          setDebugInfo(`Invalid type: ${finalType}, expected: recovery`);
          toast.error('Недействительный тип ссылки для сброса пароля.');
          setTimeout(() => navigate('/auth'), 3000);
          return;
        }

        // Устанавливаем сессию с токенами
        console.log('🔄 Setting session with tokens...');
        const { data: sessionData, error: sessionError } = await supabase.auth.setSession({
          access_token: finalAccessToken,
          refresh_token: finalRefreshToken
        });

        if (sessionError) {
          console.error('❌ Error setting session:', sessionError);
          setDebugInfo(`Session error: ${sessionError.message}`);
          toast.error('Ошибка при установке сессии: ' + sessionError.message);
          setTimeout(() => navigate('/auth'), 3000);
          return;
        }

        if (!sessionData.session) {
          console.error('❌ No session returned');
          setDebugInfo('No session returned after setting tokens');
          toast.error('Не удалось создать сессию для сброса пароля');
          setTimeout(() => navigate('/auth'), 3000);
          return;
        }

        console.log('✅ Session set successfully for:', sessionData.session.user.email);
        setDebugInfo(`Session established for: ${sessionData.session.user.email}`);
        setIsValidToken(true);
        
      } catch (error: any) {
        console.error('❌ Unexpected error:', error);
        setDebugInfo(`Unexpected error: ${error.message}`);
        toast.error('Произошла ошибка при проверке ссылки сброса пароля');
        setTimeout(() => navigate('/auth'), 3000);
      } finally {
        setIsCheckingToken(false);
      }
    };

    checkTokenAndSetSession();
  }, [searchParams, navigate]);

  const validatePasswords = () => {
    if (!newPassword || !confirmPassword) {
      toast.error('Заполните все поля');
      return false;
    }
    
    if (newPassword.length < 6) {
      toast.error('Пароль должен содержать минимум 6 символов');
      return false;
    }
    
    if (newPassword !== confirmPassword) {
      toast.error('Пароли не совпадают');
      return false;
    }
    
    return true;
  };

  const handleResetPassword = async () => {
    if (!validatePasswords()) return;
    
    setIsLoading(true);
    
    try {
      console.log('🔄 Attempting to update password...');
      
      const { data, error } = await supabase.auth.updateUser({
        password: newPassword
      });
      
      if (error) {
        console.error('❌ Password update error:', error);
        throw error;
      }
      
      console.log('✅ Password updated successfully:', data);
      toast.success('Пароль успешно изменен! Вы можете войти с новым паролем.');
      
      // Выходим из системы и перенаправляем на страницу входа
      await supabase.auth.signOut();
      
      setTimeout(() => {
        navigate('/auth');
      }, 2000);
      
    } catch (error: any) {
      console.error('❌ Error resetting password:', error);
      toast.error(error.message || 'Ошибка при смене пароля');
    } finally {
      setIsLoading(false);
    }
  };

  // Показываем загрузку пока проверяем токен
  if (isCheckingToken) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle className="text-center">Проверка ссылки...</CardTitle>
            <CardDescription className="text-center">
              Пожалуйста, подождите
            </CardDescription>
          </CardHeader>
          {debugInfo && (
            <CardContent>
              <div className="text-xs text-gray-500 bg-gray-100 p-2 rounded">
                Debug: {debugInfo}
              </div>
            </CardContent>
          )}
        </Card>
      </div>
    );
  }

  // Показываем ошибку если токен недействителен
  if (!isValidToken) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-center justify-center">
              <AlertCircle className="h-5 w-5 text-red-500" />
              Недействительная ссылка
            </CardTitle>
            <CardDescription className="text-center">
              Ссылка для сброса пароля недействительна или истекла
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {debugInfo && (
              <div className="text-xs text-gray-500 bg-gray-100 p-2 rounded">
                Debug: {debugInfo}
              </div>
            )}
            <div className="text-sm text-gray-600 bg-blue-50 p-3 rounded border border-blue-200">
              <p className="font-medium mb-2">Что проверить:</p>
              <ul className="text-xs space-y-1">
                <li>• Используйте ссылку из последнего письма</li>
                <li>• Ссылка действительна только 1 час</li>
                <li>• Не копируйте ссылку частично</li>
                <li>• Попробуйте запросить новую ссылку</li>
              </ul>
            </div>
            <Button
              variant="outline"
              onClick={() => navigate('/auth')}
              className="w-full"
            >
              Вернуться к входу
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-center justify-center">
            <Lock className="h-5 w-5" />
            Сброс пароля
          </CardTitle>
          <CardDescription className="text-center">
            Введите новый пароль для вашего аккаунта
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {debugInfo && (
            <div className="text-xs text-green-600 bg-green-50 p-2 rounded">
              ✅ {debugInfo}
            </div>
          )}
          
          <div className="space-y-2">
            <Label htmlFor="newPassword">Новый пароль</Label>
            <div className="relative">
              <Input
                id="newPassword"
                type={showPassword ? "text" : "password"}
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="Введите новый пароль (минимум 6 символов)"
                className="pr-10"
              />
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </Button>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="confirmPassword">Повторите пароль</Label>
            <div className="relative">
              <Input
                id="confirmPassword"
                type={showConfirmPassword ? "text" : "password"}
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Повторите новый пароль"
                className="pr-10"
              />
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
              >
                {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </Button>
            </div>
          </div>

          <Button 
            onClick={handleResetPassword} 
            disabled={isLoading} 
            className="w-full"
          >
            {isLoading ? 'Изменение пароля...' : 'Сменить пароль'}
          </Button>
          
          <div className="text-center">
            <Button
              variant="link"
              onClick={() => navigate('/auth')}
              className="text-sm text-gray-600"
            >
              Вернуться к входу
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ResetPasswordPage;
