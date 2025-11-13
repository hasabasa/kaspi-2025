
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "sonner";
import { useProfile } from "@/hooks/useProfile";
import { useAuth } from "@/components/integration/useAuth";
import { User, Building, Phone, Mail } from "lucide-react";

const ProfilePage = () => {
  const { user } = useAuth();
  const { profile, loading, updateProfile } = useProfile();
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    full_name: '',
    company_name: '',
    phone: ''
  });

  const handleEdit = () => {
    setFormData({
      full_name: profile?.full_name || '',
      company_name: profile?.company_name || '',
      phone: profile?.phone || ''
    });
    setIsEditing(true);
  };

  const handleSave = async () => {
    const result = await updateProfile(formData);
    if (result?.success) {
      toast.success('Профиль успешно обновлен');
      setIsEditing(false);
    } else {
      toast.error('Ошибка при обновлении профиля');
    }
  };

  const handleCancel = () => {
    setIsEditing(false);
    setFormData({
      full_name: '',
      company_name: '',
      phone: ''
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Профиль пользователя</h1>
        <p className="text-gray-500 mt-2">
          Управляйте своей учетной записью и персональными данными
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="h-5 w-5" />
              Персональная информация
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <div className="flex items-center gap-2">
                <Mail className="h-4 w-4 text-gray-400" />
                <Input
                  id="email"
                  value={user?.email || ''}
                  disabled
                  className="bg-gray-50"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="full_name">Полное имя</Label>
              <div className="flex items-center gap-2">
                <User className="h-4 w-4 text-gray-400" />
                <Input
                  id="full_name"
                  value={isEditing ? formData.full_name : (profile?.full_name || '')}
                  onChange={(e) => setFormData({...formData, full_name: e.target.value})}
                  disabled={!isEditing}
                  placeholder="Введите ваше полное имя"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="phone">Телефон</Label>
              <div className="flex items-center gap-2">
                <Phone className="h-4 w-4 text-gray-400" />
                <Input
                  id="phone"
                  value={isEditing ? formData.phone : (profile?.phone || '')}
                  onChange={(e) => setFormData({...formData, phone: e.target.value})}
                  disabled={!isEditing}
                  placeholder="+7 (xxx) xxx-xx-xx"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="company_name">Название компании</Label>
              <div className="flex items-center gap-2">
                <Building className="h-4 w-4 text-gray-400" />
                <Input
                  id="company_name"
                  value={isEditing ? formData.company_name : (profile?.company_name || '')}
                  onChange={(e) => setFormData({...formData, company_name: e.target.value})}
                  disabled={!isEditing}
                  placeholder="Введите название компании"
                />
              </div>
            </div>

            <div className="flex gap-2 pt-4">
              {!isEditing ? (
                <Button onClick={handleEdit} className="flex-1">
                  Редактировать
                </Button>
              ) : (
                <>
                  <Button onClick={handleSave} className="flex-1">
                    Сохранить
                  </Button>
                  <Button onClick={handleCancel} variant="outline" className="flex-1">
                    Отмена
                  </Button>
                </>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Информация об аккаунте</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Дата регистрации</Label>
              <p className="text-sm text-gray-600">
                {profile?.created_at ? new Date(profile.created_at).toLocaleDateString('ru-RU', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric'
                }) : 'Не указано'}
              </p>
            </div>
            
            <div className="space-y-2">
              <Label>Последнее обновление</Label>
              <p className="text-sm text-gray-600">
                {profile?.updated_at ? new Date(profile.updated_at).toLocaleDateString('ru-RU', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric'
                }) : 'Не указано'}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ProfilePage;
