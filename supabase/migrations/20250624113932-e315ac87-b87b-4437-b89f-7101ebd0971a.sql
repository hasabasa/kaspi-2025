
-- Удаляем существующее ограничение на conversion_type
ALTER TABLE public.referral_conversions DROP CONSTRAINT IF EXISTS referral_conversions_conversion_type_check;

-- Добавляем новое ограничение с правильными значениями
ALTER TABLE public.referral_conversions ADD CONSTRAINT referral_conversions_conversion_type_check 
CHECK (conversion_type IN ('registration', 'promo_code_usage', 'subscription_payment'));

-- Также убедимся, что у нас есть правильные индексы для поиска конверсий
CREATE INDEX IF NOT EXISTS idx_referral_conversions_conversion_type ON public.referral_conversions(conversion_type);
CREATE INDEX IF NOT EXISTS idx_referral_conversions_partner_conversion_type ON public.referral_conversions(partner_id, conversion_type);
