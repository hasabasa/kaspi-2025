
-- Создаем представление для статистики партнеров (без RLS)
CREATE OR REPLACE VIEW public.partner_stats AS
SELECT 
  p.id as partner_id,
  p.user_id,
  p.instagram_username,
  p.partner_code,
  -- Подсчет кликов
  COALESCE(clicks.total_clicks, 0) as total_clicks,
  -- Подсчет регистраций
  COALESCE(registrations.registrations, 0) as registrations,
  -- Подсчет использований промокодов
  COALESCE(promo_usage.promo_usage, 0) as promo_usage,
  -- Подсчет оплаченных конверсий
  COALESCE(paid_conversions.paid_conversions, 0) as paid_conversions
FROM public.partners p
LEFT JOIN (
  SELECT partner_id, COUNT(*) as total_clicks
  FROM public.referral_clicks
  GROUP BY partner_id
) clicks ON p.id = clicks.partner_id
LEFT JOIN (
  SELECT partner_id, COUNT(*) as registrations
  FROM public.referral_conversions
  WHERE conversion_type = 'registration'
  GROUP BY partner_id
) registrations ON p.id = registrations.partner_id
LEFT JOIN (
  SELECT partner_id, COUNT(*) as promo_usage
  FROM public.referral_conversions
  WHERE conversion_type = 'promo_code_usage'
  GROUP BY partner_id
) promo_usage ON p.id = promo_usage.partner_id
LEFT JOIN (
  SELECT partner_id, COUNT(*) as paid_conversions
  FROM public.referral_conversions
  WHERE conversion_type = 'subscription_payment'
  GROUP BY partner_id
) paid_conversions ON p.id = paid_conversions.partner_id;

-- Включаем RLS для таблиц (если еще не включен)
ALTER TABLE public.partners ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.referral_clicks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.referral_conversions ENABLE ROW LEVEL SECURITY;

-- Удаляем существующие политики и создаем новые
DROP POLICY IF EXISTS "Partners can view own data" ON public.partners;
DROP POLICY IF EXISTS "View clicks for own partner" ON public.referral_clicks;
DROP POLICY IF EXISTS "View conversions for own partner" ON public.referral_conversions;

-- Создаем политики заново
CREATE POLICY "Partners can view own data" 
  ON public.partners 
  FOR SELECT 
  USING (auth.uid() = user_id OR public.has_role(auth.uid(), 'admin'));

CREATE POLICY "View clicks for own partner" 
  ON public.referral_clicks 
  FOR SELECT 
  USING (
    partner_id IN (
      SELECT id FROM public.partners WHERE user_id = auth.uid()
    ) 
    OR public.has_role(auth.uid(), 'admin')
  );

CREATE POLICY "View conversions for own partner" 
  ON public.referral_conversions 
  FOR SELECT 
  USING (
    partner_id IN (
      SELECT id FROM public.partners WHERE user_id = auth.uid()
    ) 
    OR public.has_role(auth.uid(), 'admin')
  );
