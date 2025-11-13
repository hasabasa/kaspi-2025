
import { useState, useEffect } from 'react';
import { supabase } from '@/integrations/supabase/client';
import { toast } from 'sonner';

interface UserProfile {
  id: string;
  full_name: string | null;
  company_name: string | null;
  phone: string | null;
  subscription_end_date: string | null;
  bonus_days: number | null;
  created_at: string;
  roles: string[];
}

export const useUsersManagement = () => {
  const [users, setUsers] = useState<UserProfile[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadUsers();
    
    const interval = setInterval(() => {
      loadUsers(true);
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const loadUsers = async (silent = false) => {
    try {
      if (!silent) {
        setLoading(true);
      } else {
        setRefreshing(true);
      }

      console.log('Loading users...');
      
      const { data: profiles, error: profilesError } = await supabase
        .from('profiles')
        .select('*')
        .order('created_at', { ascending: false });

      if (profilesError) {
        console.error('Error loading profiles:', profilesError);
        throw profilesError;
      }

      console.log('Loaded profiles:', profiles?.length, profiles);

      const { data: userRoles, error: rolesError } = await supabase
        .from('user_roles')
        .select('user_id, role');

      if (rolesError) {
        console.error('Error loading roles:', rolesError);
        throw rolesError;
      }

      console.log('Loaded roles:', userRoles?.length);

      const usersWithRoles = profiles?.map(profile => ({
        ...profile,
        roles: userRoles?.filter(role => role.user_id === profile.id).map(role => role.role) || []
      })) || [];

      console.log('Users with roles:', usersWithRoles.length);
      setUsers(usersWithRoles);
      
      if (!silent) {
        toast.success(`Загружено ${usersWithRoles.length} пользователей`);
      }
    } catch (error) {
      console.error('Error loading users:', error);
      toast.error('Ошибка загрузки пользователей: ' + (error as Error).message);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const deleteUser = async (userId: string) => {
    try {
      const { data, error } = await supabase.rpc('delete_user_account', {
        target_user_id: userId
      });

      if (error) throw error;

      const result = data as { success: boolean; error?: string; message?: string };

      if (result.success) {
        toast.success(result.message || 'Пользователь успешно удален');
        loadUsers();
      } else {
        toast.error(result.error || 'Ошибка удаления пользователя');
      }
    } catch (error) {
      console.error('Error deleting user:', error);
      toast.error('Произошла ошибка при удалении пользователя');
    }
  };

  return {
    users,
    loading,
    refreshing,
    loadUsers,
    deleteUser
  };
};
