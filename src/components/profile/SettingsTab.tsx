
import React, { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/components/integration/useAuth";
import { toast } from "sonner";
import { Mail, Lock, AlertTriangle, Info } from "lucide-react";
import { supabase } from "@/integrations/supabase/client";

const SettingsTab = () => {
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [newEmail, setNewEmail] = useState(user?.email || '');

  const handleEmailChange = async () => {
    if (!newEmail || newEmail === user?.email) {
      toast.error('Введите новый email адрес');
      return;
    }

    setIsLoading(true);
    try {
      const { error } = await supabase.auth.updateUser({
        email: newEmail
      });

      if (error) throw error;

      toast.success('Запрос на изменение email отправлен. Проверьте почту для подтверждения.');
    } catch (error: any) {
      console.error('Error updating email:', error);
      toast.error(error.message || 'Ошибка при изменении email');
    } finally {
      setIsLoading(false);
    }
  };

  const handlePasswordReset = async () => {
    if (!user?.email) {
      toast.error('Email не найден');
      return;
    }

    setIsLoading(true);
    try {
      console.log('🔄 Sending password reset email to:', user.email);
      
      // Используем полный URL для redirectTo
      const resetUrl = `${window.location.origin}/reset-password`;
      console.log('🔗 Reset URL:', resetUrl);
      
      const { error } = await supabase.auth.resetPasswordForEmail(user.email, {
        redirectTo: resetUrl
      });

      if (error) {
        console.error('❌ Password reset error:', error);
        throw error;
      }

      console.log('✅ Password reset email sent successfully');
      toast.success('Ссылка для сброса пароля отправлена на ваш email');
    } catch (error: any) {
      console.error('❌ Error sending password reset:', error);
      toast.error(error.message || 'Ошибка при отправке ссылки сброса пароля');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Mail className="h-5 w-5" />
            Изменить Email
          </CardTitle>
          <CardDescription>
            Обновите ваш email адрес. Потребуется подтверждение на новый адрес.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="currentEmail">Текущий email</Label>
            <Input
              id="currentEmail"
              value={user?.email || ''}
              disabled
              className="bg-gray-50"
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="newEmail">Новый email</Label>
            <Input
              id="newEmail"
              type="email"
              value={newEmail}
              onChange={(e) => setNewEmail(e.target.value)}
              placeholder="Введите новый email"
            />
          </div>
          
          <Button onClick={handleEmailChange} disabled={isLoading} className="w-full">
            {isLoading ? 'Отправка...' : 'Изменить Email'}
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Lock className="h-5 w-5" />
            Сброс пароля
          </CardTitle>
          <CardDescription>
            Отправить ссылку для сброса пароля на ваш email.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-start gap-3 p-3 bg-blue-50 border border-blue-200 rounded-md">
            <Info className="h-5 w-5 text-blue-600 mt-0.5" />
            <div className="text-sm text-blue-800">
              <p className="font-medium">Инструкция</p>
              <ul className="mt-1 space-y-1 text-xs">
                <li>• Ссылка будет отправлена на ваш текущий email</li>
                <li>• Ссылка действительна в течение 1 часа</li>
                <li>• Откройте ссылку в том же браузере</li>
                <li>• Если ссылка не работает, запросите новую</li>
              </ul>
            </div>
          </div>

          <div className="flex items-start gap-3 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
            <AlertTriangle className="h-5 w-5 text-yellow-600 mt-0.5" />
            <div className="text-sm text-yellow-800">
              <p className="font-medium">Внимание</p>
              <p>После сброса пароля вам потребуется войти в систему заново.</p>
            </div>
          </div>
          
          <Button 
            onClick={handlePasswordReset} 
            disabled={isLoading} 
            variant="outline" 
            className="w-full"
          >
            {isLoading ? 'Отправка...' : 'Отправить ссылку сброса пароля'}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
};

export default SettingsTab;
