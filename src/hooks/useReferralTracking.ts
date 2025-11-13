
import { useEffect } from 'react';
import { supabase } from '@/integrations/supabase/client';

export const useReferralTracking = () => {
  useEffect(() => {
    const trackReferral = async () => {
      const urlParams = new URLSearchParams(window.location.search);
      const partnerCode = urlParams.get('ref') || urlParams.get('partner');
      
      if (partnerCode) {
        console.log('Tracking referral for partner:', partnerCode);
        
        try {
          const referralData = {
            partner_code: partnerCode,
            url: window.location.href,
            utm_source: urlParams.get('utm_source'),
            utm_medium: urlParams.get('utm_medium'),
            utm_campaign: urlParams.get('utm_campaign'),
            utm_content: urlParams.get('utm_content'),
            utm_term: urlParams.get('utm_term'),
          };

          console.log('Sending referral data:', referralData);

          // Call Edge Function with proper body
          const { data, error } = await supabase.functions.invoke('track-referral', {
            body: referralData
          });

          if (error) {
            console.error('Error tracking referral:', error);
          } else {
            console.log('Referral tracked successfully:', data);
            
            // Store referral data in localStorage for future use
            const storedData = {
              ...referralData,
              click_id: data?.clickId,
              partner_id: data?.partnerId,
              timestamp: new Date().toISOString()
            };
            
            localStorage.setItem('referral_data', JSON.stringify(storedData));
            console.log('Referral data stored in localStorage:', storedData);
          }
        } catch (error) {
          console.error('Error calling track-referral function:', error);
        }
      } else {
        console.log('No partner code found in URL');
      }
    };

    trackReferral();
  }, []);

  const getReferralData = () => {
    const stored = localStorage.getItem('referral_data');
    if (stored) {
      try {
        return JSON.parse(stored);
      } catch (error) {
        console.error('Error parsing referral data:', error);
        return null;
      }
    }
    return null;
  };

  const clearReferralData = () => {
    localStorage.removeItem('referral_data');
    console.log('Referral data cleared from localStorage');
  };

  return {
    getReferralData,
    clearReferralData
  };
};
