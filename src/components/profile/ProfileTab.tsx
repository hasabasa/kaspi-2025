
import React, { useState, useRef } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { useAuth } from "@/components/integration/useAuth";
import { useProfile } from "@/hooks/useProfile";
import { toast } from "sonner";
import { User, Upload } from "lucide-react";
import { supabase } from "@/integrations/supabase/client";

const ProfileTab = () => {
  const { user } = useAuth();
  const { profile, updateProfile } = useProfile();
  const [isLoading, setIsLoading] = useState(false);
  const [fullName, setFullName] = useState(profile?.full_name || '');
  const [avatarUrl, setAvatarUrl] = useState<string>('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleAvatarUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file || !user) return;

    setIsLoading(true);
    try {
      const fileExt = file.name.split('.').pop();
      const fileName = `${user.id}.${fileExt}`;
      const filePath = `avatars/${fileName}`;

      const { error: uploadError } = await supabase.storage
        .from('avatars')
        .upload(filePath, file, { upsert: true });

      if (uploadError) throw uploadError;

      const { data: { publicUrl } } = supabase.storage
        .from('avatars')
        .getPublicUrl(filePath);

      setAvatarUrl(publicUrl);
      toast.success('Аватар успешно загружен');
    } catch (error) {
      console.error('Error uploading avatar:', error);
      toast.error('Ошибка при загрузке аватара');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    if (!user) return;

    setIsLoading(true);
    try {
      const updateData: any = {
        full_name: fullName
      };

      if (avatarUrl) {
        updateData.avatar_url = avatarUrl;
      }

      const result = await updateProfile(updateData);
      if (result?.success) {
        toast.success('Профиль успешно обновлен');
      } else {
        toast.error('Ошибка при обновлении профиля');
      }
    } catch (error) {
      console.error('Error updating profile:', error);
      toast.error('Ошибка при обновлении профиля');
    } finally {
      setIsLoading(false);
    }
  };

  const getAvatarUrl = () => {
    if (avatarUrl) return avatarUrl;
    return profile?.avatar_url || '';
  };

  const getInitials = () => {
    const name = fullName || profile?.full_name || user?.email || '';
    return name
      .split(' ')
      .map(word => word.charAt(0))
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col items-center space-y-4">
        <div className="relative">
          <Avatar className="h-24 w-24">
            <AvatarImage src={getAvatarUrl()} alt="Avatar" />
            <AvatarFallback className="text-lg">
              {getInitials() || <User className="h-8 w-8" />}
            </AvatarFallback>
          </Avatar>
          <Button
            size="sm"
            variant="outline"
            className="absolute -bottom-2 -right-2 h-8 w-8 rounded-full p-0"
            onClick={() => fileInputRef.current?.click()}
            disabled={isLoading}
          >
            <Upload className="h-4 w-4" />
          </Button>
        </div>
        
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleAvatarUpload}
          className="hidden"
        />
        
        <p className="text-sm text-gray-500">
          Нажмите на иконку, чтобы изменить аватар
        </p>
      </div>

      <div className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            value={user?.email || ''}
            disabled
            className="bg-gray-50"
          />
          <p className="text-xs text-gray-500">
            Email можно изменить в разделе "Настройки"
          </p>
        </div>

        <div className="space-y-2">
          <Label htmlFor="fullName">Полное имя</Label>
          <Input
            id="fullName"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            placeholder="Введите ваше полное имя"
          />
        </div>
      </div>

      <div className="flex justify-end">
        <Button onClick={handleSave} disabled={isLoading}>
          {isLoading ? 'Сохранение...' : 'Сохранить изменения'}
        </Button>
      </div>
    </div>
  );
};

export default ProfileTab;
