import { supabase } from '@/integrations/supabase/client';
import { useToast } from '@/components/ui/use-toast';

export const useReferralConversion = () => {
  const { toast } = useToast();

  const recordConversion = async (
    userId: string,
    conversionType: 'registration' | 'promo_code_usage' | 'subscription_payment',
    amount?: number,
    promoCodeId?: string
  ) => {
    try {
      console.log('Recording conversion:', { userId, conversionType, amount, promoCodeId });

      // Get referral data from localStorage
      const referralDataStr = localStorage.getItem('referral_data');
      if (!referralDataStr) {
        console.log('No referral data found in localStorage');
        return;
      }

      const referralData = JSON.parse(referralDataStr);
      console.log('Using referral data:', referralData);

      if (!referralData.partner_code) {
        console.log('No partner code in referral data');
        return;
      }

      // Find partner by code with detailed logging
      console.log('Looking for partner with code:', referralData.partner_code);
      const { data: partner, error: partnerError } = await supabase
        .from('partners')
        .select('id, commission_rate, partner_code, is_active')
        .eq('partner_code', referralData.partner_code)
        .eq('is_active', true)
        .single();

      if (partnerError) {
        console.error('Partner query error:', partnerError);
        return;
      }

      if (!partner) {
        console.error('Partner not found for code:', referralData.partner_code);
        return;
      }

      console.log('Found partner for conversion:', partner);

      // Calculate commission
      const commissionRate = partner.commission_rate || 10;
      const commissionEarned = amount ? (amount * commissionRate / 100) : 0;

      console.log('Commission calculation:', { amount, commissionRate, commissionEarned });

      // Record conversion with explicit status
      const conversionData = {
        partner_id: partner.id,
        user_id: userId,
        promo_code_id: promoCodeId || null,
        referral_click_id: referralData.click_id || null,
        conversion_type: conversionType,
        amount: amount || 0,
        commission_earned: commissionEarned,
        status: 'confirmed',
        notes: `Conversion from ${referralData.utm_source || 'unknown source'} - ${conversionType} - Partner: ${partner.partner_code}`
      };

      console.log('Inserting conversion with data:', conversionData);

      const { data: insertedData, error: conversionError } = await supabase
        .from('referral_conversions')
        .insert(conversionData)
        .select()
        .single();

      if (conversionError) {
        console.error('Error recording conversion:', conversionError);
        throw conversionError;
      }

      console.log('Conversion recorded successfully:', insertedData);
      
      // Show success toast for important conversions
      if (conversionType === 'registration') {
        console.log('Registration conversion recorded for partner:', partner.partner_code);
        toast({
          title: "Добро пожаловать!",
          description: "Регистрация завершена через партнерскую ссылку"
        });
      } else if (conversionType === 'subscription_payment') {
        toast({
          title: "Оплата прошла успешно",
          description: "Спасибо за подписку!"
        });
      }

      // Don't clear referral data immediately - keep it for potential future conversions
      console.log('Keeping referral data for potential future conversions');
      
      return insertedData;
    } catch (error) {
      console.error('Error in recordConversion:', error);
      throw error;
    }
  };

  return {
    recordConversion
  };
};
