
import { useState, useEffect } from 'react';
import { supabase } from '@/integrations/supabase/client';
import { useAuth } from '@/components/integration/useAuth';

export const useUserRole = () => {
  const { user, loading: authLoading } = useAuth();
  const [roles, setRoles] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (authLoading) {
      console.log('useUserRole: Auth still loading, waiting...');
      return;
    }

    if (user) {
      console.log('useUserRole: Loading roles for user:', user.email);
      loadUserRoles();
    } else {
      console.log('useUserRole: No user found, clearing roles');
      setRoles([]);
      setError(null);
      setLoading(false);
    }
  }, [user, authLoading]);

  const loadUserRoles = async () => {
    if (!user) {
      console.log('useUserRole: No user for role loading');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      console.log('useUserRole: Fetching roles for user ID:', user.id);
      
      const { data, error } = await supabase
        .from('user_roles')
        .select('role')
        .eq('user_id', user.id);
      
      if (error) {
        console.error('useUserRole: Database error:', error);
        throw error;
      }
      
      const userRoles = data?.map(r => r.role) || [];
      console.log('useUserRole: Loaded roles:', userRoles);
      
      setRoles(userRoles);
    } catch (error) {
      console.error('useUserRole: Error loading user roles:', error);
      setError(error instanceof Error ? error.message : 'Unknown error');
      setRoles([]);
    } finally {
      setLoading(false);
    }
  };

  const hasRole = (role: string) => {
    const result = roles.includes(role);
    console.log(`useUserRole: Checking role '${role}':`, result, 'Available roles:', roles);
    return result;
  };
  
  const isAdmin = hasRole('admin');
  const isPartner = hasRole('partner');

  console.log('useUserRole: Current state - loading:', loading, 'roles:', roles, 'isAdmin:', isAdmin, 'isPartner:', isPartner);

  return {
    roles,
    loading,
    error,
    hasRole,
    isAdmin,
    isPartner,
    refetchRoles: loadUserRoles
  };
};
