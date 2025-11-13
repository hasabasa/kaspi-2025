
import { useState, useEffect } from 'react';
import { supabase } from '@/integrations/supabase/client';
import { useAuth } from '@/components/integration/useAuth';

interface UserProfile {
  id: string;
  full_name: string | null;
  company_name: string | null;
  phone: string | null;
  avatar_url: string | null;
  subscription_end_date: string | null;
  bonus_days: number;
  has_paid_subscription: boolean | null;
  created_at: string;
  updated_at: string;
}

interface SubscriptionStatus {
  isActive: boolean;
  daysLeft: number;
  status: 'active' | 'expired' | 'trial';
  plan: 'free' | 'pro';
  hasPaidSubscription: boolean;
}

interface PromoCodeResult {
  success: boolean;
  message?: string;
  error?: string;
  bonus_days?: number;
  new_end_date?: string;
}

export const useProfile = () => {
  const { user } = useAuth();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      loadProfile();
    } else {
      setProfile(null);
      setLoading(false);
    }
  }, [user]);

  const loadProfile = async () => {
    if (!user) return;
    
    try {
      const { data, error } = await supabase
        .from('profiles')
        .select('id, full_name, company_name, phone, avatar_url, subscription_end_date, bonus_days, has_paid_subscription, created_at, updated_at')
        .eq('id', user.id)
        .single();
      
      if (error) throw error;
      
      if (data) {
        // Создаем объект только с нужными полями
        const profileData: UserProfile = {
          id: data.id,
          full_name: data.full_name,
          company_name: data.company_name,
          phone: data.phone,
          avatar_url: data.avatar_url,
          subscription_end_date: data.subscription_end_date,
          bonus_days: data.bonus_days || 0,
          has_paid_subscription: data.has_paid_subscription,
          created_at: data.created_at,
          updated_at: data.updated_at
        };
        
        setProfile(profileData);
      }
    } catch (error) {
      console.error('Error loading profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateProfile = async (updates: Partial<UserProfile>) => {
    if (!user) return;
    
    try {
      const { data, error } = await supabase
        .from('profiles')
        .update(updates)
        .eq('id', user.id)
        .select('id, full_name, company_name, phone, avatar_url, subscription_end_date, bonus_days, has_paid_subscription, created_at, updated_at')
        .single();
      
      if (error) throw error;
      
      if (data) {
        // Создаем объект только с нужными полями
        const profileData: UserProfile = {
          id: data.id,
          full_name: data.full_name,
          company_name: data.company_name,
          phone: data.phone,
          avatar_url: data.avatar_url,
          subscription_end_date: data.subscription_end_date,
          bonus_days: data.bonus_days || 0,
          has_paid_subscription: data.has_paid_subscription,
          created_at: data.created_at,
          updated_at: data.updated_at
        };
        
        setProfile(profileData);
        return { success: true, data: profileData };
      }
    } catch (error) {
      console.error('Error updating profile:', error);
      return { success: false, error };
    }
  };

  const applyPromoCode = async (promoCode: string): Promise<PromoCodeResult> => {
    if (!user) return { success: false, error: 'Пользователь не авторизован' };
    
    try {
      const { data, error } = await supabase.rpc('apply_promo_code', {
        p_user_id: user.id,
        p_promo_code: promoCode
      });
      
      if (error) throw error;
      
      const result = data as unknown as PromoCodeResult;
      
      if (result.success) {
        await loadProfile(); // Перезагружаем профиль после применения промокода
      }
      
      return result;
    } catch (error) {
      console.error('Error applying promo code:', error);
      return { success: false, error: 'Ошибка при применении промокода' };
    }
  };

  const getSubscriptionStatus = (): SubscriptionStatus => {
    if (!profile || !profile.subscription_end_date) {
      return {
        isActive: false,
        daysLeft: 0,
        status: 'expired',
        plan: 'free',
        hasPaidSubscription: !!profile?.has_paid_subscription
      };
    }

    const endDate = new Date(profile.subscription_end_date);
    const now = new Date();
    const timeDiff = endDate.getTime() - now.getTime();
    const daysLeft = Math.ceil(timeDiff / (1000 * 3600 * 24));

    const isActive = daysLeft > 0;
    
    return {
      isActive,
      daysLeft: Math.max(0, daysLeft),
      status: isActive ? 'trial' : 'expired',
      plan: 'free', // В данный момент у нас только бесплатный план с пробным периодом
      hasPaidSubscription: !!profile.has_paid_subscription
    };
  };

  return {
    profile,
    loading,
    updateProfile,
    refetchProfile: loadProfile,
    applyPromoCode,
    subscriptionStatus: getSubscriptionStatus()
  };
};
