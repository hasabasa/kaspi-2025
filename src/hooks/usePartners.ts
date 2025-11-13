
import { useState, useEffect } from 'react';
import { supabase } from '@/integrations/supabase/client';
import { useToast } from '@/components/ui/use-toast';

interface Partner {
  id: string;
  user_id: string;
  partner_code: string;
  instagram_username: string;
  company_name: string | null;
  contact_email: string | null;
  commission_rate: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export const usePartners = () => {
  const [partners, setPartners] = useState<Partner[]>([]);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    loadPartners();
  }, []);

  const loadPartners = async () => {
    try {
      const { data, error } = await supabase
        .from('partners')
        .select('*')
        .order('created_at', { ascending: false });
      
      if (error) throw error;
      setPartners(data || []);
    } catch (error) {
      console.error('Error loading partners:', error);
      toast({
        title: "Ошибка",
        description: "Не удалось загрузить список партнеров",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const createPartner = async (partnerData: {
    login: string;
    password: string;
    fullName: string;
  }) => {
    try {
      console.log('Creating partner with data:', { ...partnerData, password: '[HIDDEN]' });
      
      const { data, error } = await supabase.functions.invoke('create-partner', {
        body: partnerData,
      });

      console.log('Supabase function response:', data);

      if (error) {
        console.error('Supabase function error:', error);
        throw new Error(error.message || 'Ошибка вызова функции');
      }

      if (!data.success) {
        console.error('Function returned error:', data.error);
        throw new Error(data.error || 'Неизвестная ошибка');
      }

      await loadPartners();
      
      toast({
        title: "Успех",
        description: `Партнер создан успешно. Email: ${data.generatedEmail || data.email}`
      });

      return { success: true };
    } catch (error) {
      console.error('Error creating partner:', error);
      const errorMessage = error instanceof Error ? error.message : "Не удалось создать партнера";
      toast({
        title: "Ошибка создания партнера",
        description: errorMessage,
        variant: "destructive"
      });
      return { success: false, error };
    }
  };

  const updatePartner = async (id: string, updates: Partial<Partner>) => {
    try {
      const { error } = await supabase
        .from('partners')
        .update(updates)
        .eq('id', id);
      
      if (error) throw error;
      
      await loadPartners();
      
      toast({
        title: "Успех",
        description: "Партнер обновлен"
      });
    } catch (error) {
      console.error('Error updating partner:', error);
      toast({
        title: "Ошибка",
        description: "Не удалось обновить партнера",
        variant: "destructive"
      });
    }
  };

  return {
    partners,
    loading,
    createPartner,
    updatePartner,
    refetchPartners: loadPartners
  };
};
