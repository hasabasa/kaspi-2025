
-- Drop the existing view
DROP VIEW IF EXISTS public.partner_stats;

-- Recreate the view without SECURITY DEFINER (views don't support RLS directly)
CREATE VIEW public.partner_stats AS
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

-- Add RLS policies to the underlying tables to ensure proper security
-- Enable RLS on partners table if not already enabled
ALTER TABLE public.partners ENABLE ROW LEVEL SECURITY;

-- Policy for admins to see all partners
CREATE POLICY "Admins can view all partners" 
  ON public.partners 
  FOR SELECT 
  USING (public.has_role(auth.uid(), 'admin'));

-- Policy for partners to see only their own record
CREATE POLICY "Partners can view their own record" 
  ON public.partners 
  FOR SELECT 
  USING (user_id = auth.uid());

-- Enable RLS on referral_links table if not already enabled
ALTER TABLE public.referral_links ENABLE ROW LEVEL SECURITY;

-- Policy for admins to see all referral links
CREATE POLICY "Admins can view all referral links" 
  ON public.referral_links 
  FOR SELECT 
  USING (public.has_role(auth.uid(), 'admin'));

-- Policy for partners to see only their own referral links
CREATE POLICY "Partners can view their own referral links" 
  ON public.referral_links 
  FOR SELECT 
  USING (
    EXISTS (
      SELECT 1 FROM public.partners 
      WHERE id = referral_links.partner_id 
      AND user_id = auth.uid()
    )
  );

-- Enable RLS on referral_conversions table if not already enabled
ALTER TABLE public.referral_conversions ENABLE ROW LEVEL SECURITY;

-- Policy for admins to see all referral conversions
CREATE POLICY "Admins can view all referral conversions" 
  ON public.referral_conversions 
  FOR SELECT 
  USING (public.has_role(auth.uid(), 'admin'));

-- Policy for partners to see only their own referral conversions
CREATE POLICY "Partners can view their own referral conversions" 
  ON public.referral_conversions 
  FOR SELECT 
  USING (
    EXISTS (
      SELECT 1 FROM public.partners 
      WHERE id = referral_conversions.partner_id 
      AND user_id = auth.uid()
    )
  );

-- Enable RLS on promo_codes table if not already enabled
ALTER TABLE public.promo_codes ENABLE ROW LEVEL SECURITY;

-- Policy for admins to see all promo codes
CREATE POLICY "Admins can view all promo codes" 
  ON public.promo_codes 
  FOR SELECT 
  USING (public.has_role(auth.uid(), 'admin'));

-- Policy for partners to see only their own promo codes
CREATE POLICY "Partners can view their own promo codes" 
  ON public.promo_codes 
  FOR SELECT 
  USING (
    partner_id IS NULL OR EXISTS (
      SELECT 1 FROM public.partners 
      WHERE id = promo_codes.partner_id 
      AND user_id = auth.uid()
    )
  );
