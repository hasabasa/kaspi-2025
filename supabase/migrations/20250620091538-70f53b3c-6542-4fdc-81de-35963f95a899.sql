
-- Добавляем поле instagram_username в таблицу partners
ALTER TABLE public.partners 
ADD COLUMN IF NOT EXISTS instagram_username TEXT UNIQUE;

-- Обновляем существующие записи (если есть) временными значениями
UPDATE public.partners 
SET instagram_username = 'temp_' || SUBSTRING(partner_code FROM 9)
WHERE instagram_username IS NULL;

-- Делаем instagram_username обязательным полем
ALTER TABLE public.partners 
ALTER COLUMN instagram_username SET NOT NULL;

-- Создаем функцию для генерации промокода из Instagram username
CREATE OR REPLACE FUNCTION public.generate_partner_code(instagram_name TEXT)
RETURNS TEXT
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN 'PARTNER_' || UPPER(instagram_name);
END;
$$;

-- Добавляем индексы для оптимизации запросов статистики
CREATE INDEX IF NOT EXISTS idx_referral_links_partner_created 
ON public.referral_links(partner_id, created_at);

CREATE INDEX IF NOT EXISTS idx_referral_conversions_partner_type 
ON public.referral_conversions(partner_id, conversion_type);

CREATE INDEX IF NOT EXISTS idx_promo_codes_partner_usage 
ON public.promo_codes(partner_id, usage_count);

-- Создаем представление для статистики партнеров (без RLS)
CREATE OR REPLACE VIEW public.partner_stats AS
SELECT 
  p.id as partner_id,
  p.user_id,
  p.instagram_username,
  p.partner_code,
  COALESCE(link_stats.total_clicks, 0) as total_clicks,
  COALESCE(conversion_stats.registrations, 0) as registrations,
  COALESCE(promo_stats.promo_usage, 0) as promo_usage,
  COALESCE(conversion_stats.paid_conversions, 0) as paid_conversions
FROM public.partners p
LEFT JOIN (
  SELECT 
    partner_id, 
    COUNT(*) as total_clicks
  FROM public.referral_links 
  GROUP BY partner_id
) link_stats ON p.id = link_stats.partner_id
LEFT JOIN (
  SELECT 
    partner_id,
    COUNT(CASE WHEN conversion_type = 'registration' THEN 1 END) as registrations,
    COUNT(CASE WHEN conversion_type = 'payment' THEN 1 END) as paid_conversions
  FROM public.referral_conversions 
  GROUP BY partner_id
) conversion_stats ON p.id = conversion_stats.partner_id
LEFT JOIN (
  SELECT 
    partner_id,
    SUM(usage_count) as promo_usage
  FROM public.promo_codes 
  GROUP BY partner_id
) promo_stats ON p.id = promo_stats.partner_id;
