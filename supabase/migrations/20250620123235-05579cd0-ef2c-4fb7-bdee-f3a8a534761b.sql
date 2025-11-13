
-- Создаем таблицу для отслеживания кликов по партнерским ссылкам
CREATE TABLE public.referral_clicks (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  partner_id UUID NOT NULL REFERENCES public.partners(id) ON DELETE CASCADE,
  visitor_ip INET,
  user_agent TEXT,
  referrer TEXT,
  utm_source TEXT,
  utm_medium TEXT,
  utm_campaign TEXT,
  utm_content TEXT,
  utm_term TEXT,
  page_url TEXT,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Создаем индексы для оптимизации запросов
CREATE INDEX idx_referral_clicks_partner_id ON public.referral_clicks(partner_id);
CREATE INDEX idx_referral_clicks_created_at ON public.referral_clicks(created_at);
CREATE INDEX idx_referral_clicks_utm_source ON public.referral_clicks(utm_source);

-- Обновляем таблицу referral_conversions для поддержки разных типов конверсий
ALTER TABLE public.referral_conversions 
ADD COLUMN IF NOT EXISTS referral_click_id UUID REFERENCES public.referral_clicks(id),
ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'pending',
ADD COLUMN IF NOT EXISTS notes TEXT;

-- Обновляем таблицу profiles для сохранения UTM параметров при регистрации
ALTER TABLE public.profiles 
ADD COLUMN IF NOT EXISTS utm_source TEXT,
ADD COLUMN IF NOT EXISTS utm_medium TEXT,
ADD COLUMN IF NOT EXISTS utm_campaign TEXT,
ADD COLUMN IF NOT EXISTS utm_content TEXT,
ADD COLUMN IF NOT EXISTS utm_term TEXT;

-- Создаем индексы для быстрого поиска по UTM параметрам
CREATE INDEX IF NOT EXISTS idx_profiles_utm_source ON public.profiles(utm_source);
CREATE INDEX IF NOT EXISTS idx_profiles_referral_source ON public.profiles(referral_source);

-- Включаем RLS для новой таблицы
ALTER TABLE public.referral_clicks ENABLE ROW LEVEL SECURITY;

-- Создаем политики RLS для таблицы referral_clicks (только админы и партнеры могут видеть свои клики)
CREATE POLICY "Admins can view all referral clicks" 
  ON public.referral_clicks 
  FOR SELECT 
  USING (
    EXISTS (
      SELECT 1 FROM public.user_roles 
      WHERE user_id = auth.uid() AND role = 'admin'
    )
  );

CREATE POLICY "Partners can view their own referral clicks" 
  ON public.referral_clicks 
  FOR SELECT 
  USING (
    EXISTS (
      SELECT 1 FROM public.partners 
      WHERE id = partner_id AND user_id = auth.uid()
    )
  );

-- Обновляем функцию handle_new_user для сохранения UTM параметров
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  INSERT INTO public.profiles (
    id, 
    full_name, 
    company_name, 
    phone,
    subscription_end_date,
    bonus_days,
    referral_source,
    utm_source,
    utm_medium,
    utm_campaign,
    utm_content,
    utm_term
  )
  VALUES (
    NEW.id, 
    NEW.raw_user_meta_data->>'full_name', 
    NEW.raw_user_meta_data->>'company_name',
    NEW.raw_user_meta_data->>'phone',
    NOW() + INTERVAL '3 days',
    0,
    NEW.raw_user_meta_data->>'referral_source',
    NEW.raw_user_meta_data->>'utm_source',
    NEW.raw_user_meta_data->>'utm_medium',
    NEW.raw_user_meta_data->>'utm_campaign',
    NEW.raw_user_meta_data->>'utm_content',
    NEW.raw_user_meta_data->>'utm_term'
  )
  ON CONFLICT (id) DO UPDATE SET
    full_name = COALESCE(NEW.raw_user_meta_data->>'full_name', profiles.full_name),
    company_name = COALESCE(NEW.raw_user_meta_data->>'company_name', profiles.company_name),
    phone = COALESCE(NEW.raw_user_meta_data->>'phone', profiles.phone),
    subscription_end_date = COALESCE(profiles.subscription_end_date, NOW() + INTERVAL '3 days'),
    referral_source = COALESCE(NEW.raw_user_meta_data->>'referral_source', profiles.referral_source),
    utm_source = COALESCE(NEW.raw_user_meta_data->>'utm_source', profiles.utm_source),
    utm_medium = COALESCE(NEW.raw_user_meta_data->>'utm_medium', profiles.utm_medium),
    utm_campaign = COALESCE(NEW.raw_user_meta_data->>'utm_campaign', profiles.utm_campaign),
    utm_content = COALESCE(NEW.raw_user_meta_data->>'utm_content', profiles.utm_content),
    utm_term = COALESCE(NEW.raw_user_meta_data->>'utm_term', profiles.utm_term),
    updated_at = now();
  
  RETURN NEW;
END;
$$;
