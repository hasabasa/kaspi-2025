
-- Создание системы ролей и реферальной программы

-- 1. Создаем enum для ролей
CREATE TYPE public.app_role AS ENUM ('admin', 'partner', 'user');

-- 2. Таблица ролей пользователей
CREATE TABLE public.user_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    role app_role NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    UNIQUE (user_id, role)
);

-- 3. Таблица партнеров
CREATE TABLE public.partners (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL UNIQUE,
    partner_code TEXT UNIQUE NOT NULL,
    company_name TEXT,
    contact_email TEXT,
    commission_rate DECIMAL(5,2) DEFAULT 10.00,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- 4. Таблица промокодов
CREATE TABLE public.promo_codes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT UNIQUE NOT NULL,
    partner_id UUID REFERENCES public.partners(id) ON DELETE CASCADE,
    bonus_days INTEGER DEFAULT 15,
    is_active BOOLEAN DEFAULT true,
    usage_count INTEGER DEFAULT 0,
    max_usage INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    expires_at TIMESTAMP WITH TIME ZONE
);

-- 5. Таблица переходов по реферальным ссылкам
CREATE TABLE public.referral_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    partner_id UUID REFERENCES public.partners(id) ON DELETE CASCADE NOT NULL,
    visitor_ip TEXT,
    user_agent TEXT,
    referrer TEXT,
    utm_source TEXT,
    utm_medium TEXT,
    utm_campaign TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- 6. Таблица конверсий
CREATE TABLE public.referral_conversions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    partner_id UUID REFERENCES public.partners(id) ON DELETE CASCADE NOT NULL,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    promo_code_id UUID REFERENCES public.promo_codes(id) ON DELETE SET NULL,
    conversion_type TEXT CHECK (conversion_type IN ('registration', 'subscription', 'payment')),
    amount DECIMAL(10,2),
    commission_earned DECIMAL(10,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- 7. Обновляем таблицу profiles для бонусов подписки
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS subscription_end_date TIMESTAMP WITH TIME ZONE;
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS bonus_days INTEGER DEFAULT 0;
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS referral_source TEXT;

-- 8. Функция для проверки ролей (SECURITY DEFINER для избежания рекурсии RLS)
CREATE OR REPLACE FUNCTION public.has_role(_user_id UUID, _role app_role)
RETURNS BOOLEAN
LANGUAGE SQL
STABLE
SECURITY DEFINER
AS $$
  SELECT EXISTS (
    SELECT 1
    FROM public.user_roles
    WHERE user_id = _user_id
      AND role = _role
  )
$$;

-- 9. Включаем RLS для всех таблиц
ALTER TABLE public.user_roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.partners ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.promo_codes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.referral_links ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.referral_conversions ENABLE ROW LEVEL SECURITY;

-- 10. RLS политики для user_roles
CREATE POLICY "Users can view own roles" 
  ON public.user_roles 
  FOR SELECT 
  USING (auth.uid() = user_id OR public.has_role(auth.uid(), 'admin'));

CREATE POLICY "Only admins can manage roles" 
  ON public.user_roles 
  FOR ALL 
  USING (public.has_role(auth.uid(), 'admin'));

-- 11. RLS политики для partners
CREATE POLICY "Partners can view own data" 
  ON public.partners 
  FOR SELECT 
  USING (auth.uid() = user_id OR public.has_role(auth.uid(), 'admin'));

CREATE POLICY "Only admins can manage partners" 
  ON public.partners 
  FOR INSERT 
  WITH CHECK (public.has_role(auth.uid(), 'admin'));

CREATE POLICY "Admins and partners can update partner data" 
  ON public.partners 
  FOR UPDATE 
  USING (auth.uid() = user_id OR public.has_role(auth.uid(), 'admin'));

-- 12. RLS политики для promo_codes
CREATE POLICY "Partners can view own promo codes" 
  ON public.promo_codes 
  FOR SELECT 
  USING (
    EXISTS (
      SELECT 1 FROM public.partners 
      WHERE id = promo_codes.partner_id 
      AND user_id = auth.uid()
    ) OR public.has_role(auth.uid(), 'admin')
  );

CREATE POLICY "Only admins can manage promo codes" 
  ON public.promo_codes 
  FOR ALL 
  USING (public.has_role(auth.uid(), 'admin'));

-- 13. RLS политики для referral_links
CREATE POLICY "Partners can view own referral links" 
  ON public.referral_links 
  FOR SELECT 
  USING (
    EXISTS (
      SELECT 1 FROM public.partners 
      WHERE id = referral_links.partner_id 
      AND user_id = auth.uid()
    ) OR public.has_role(auth.uid(), 'admin')
  );

-- 14. RLS политики для referral_conversions
CREATE POLICY "Partners can view own conversions" 
  ON public.referral_conversions 
  FOR SELECT 
  USING (
    EXISTS (
      SELECT 1 FROM public.partners 
      WHERE id = referral_conversions.partner_id 
      AND user_id = auth.uid()
    ) OR public.has_role(auth.uid(), 'admin')
  );

-- 15. Триггеры для updated_at
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_partners_updated_at 
  BEFORE UPDATE ON public.partners 
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

-- 16. Создаем первого админа (замените email на ваш)
-- Раскомментируйте после создания пользователя
-- INSERT INTO public.user_roles (user_id, role) 
-- SELECT id, 'admin'::app_role 
-- FROM auth.users 
-- WHERE email = 'your-admin-email@example.com' 
-- LIMIT 1;
