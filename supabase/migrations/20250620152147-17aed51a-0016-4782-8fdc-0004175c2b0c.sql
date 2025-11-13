
-- Drop the existing view first
DROP VIEW IF EXISTS public.partner_stats;

-- Recreate the view without SECURITY DEFINER (views don't support this)
CREATE VIEW public.partner_stats AS
SELECT 
  p.id as partner_id,
  p.user_id,
  p.instagram_username,
  p.partner_code,
  COALESCE(click_stats.total_clicks, 0) as total_clicks,
  COALESCE(conversion_stats.registrations, 0) as registrations,
  COALESCE(promo_stats.promo_usage, 0) as promo_usage,
  COALESCE(conversion_stats.paid_conversions, 0) as paid_conversions
FROM public.partners p
LEFT JOIN (
  SELECT 
    partner_id, 
    COUNT(*) as total_clicks
  FROM public.referral_clicks 
  GROUP BY partner_id
) click_stats ON p.id = click_stats.partner_id
LEFT JOIN (
  SELECT 
    partner_id,
    COUNT(CASE WHEN conversion_type = 'registration' THEN 1 END) as registrations,
    COUNT(CASE WHEN conversion_type = 'subscription_payment' THEN 1 END) as paid_conversions
  FROM public.referral_conversions 
  GROUP BY partner_id
) conversion_stats ON p.id = conversion_stats.partner_id
LEFT JOIN (
  SELECT 
    partner_id,
    SUM(usage_count) as promo_usage
  FROM public.promo_codes 
  WHERE partner_id IS NOT NULL
  GROUP BY partner_id
) promo_stats ON p.id = promo_stats.partner_id;
