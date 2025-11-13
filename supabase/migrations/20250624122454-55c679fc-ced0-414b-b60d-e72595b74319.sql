
-- Обновляем функцию handle_new_user() для установки 5-дневного пробного периода вместо 3-дневного
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
AS $function$
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
    NOW() + INTERVAL '5 days', -- Изменено с 3 на 5 дней
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
    subscription_end_date = COALESCE(profiles.subscription_end_date, NOW() + INTERVAL '5 days'), -- Изменено с 3 на 5 дней
    referral_source = COALESCE(NEW.raw_user_meta_data->>'referral_source', profiles.referral_source),
    utm_source = COALESCE(NEW.raw_user_meta_data->>'utm_source', profiles.utm_source),
    utm_medium = COALESCE(NEW.raw_user_meta_data->>'utm_medium', profiles.utm_medium),
    utm_campaign = COALESCE(NEW.raw_user_meta_data->>'utm_campaign', profiles.utm_campaign),
    utm_content = COALESCE(NEW.raw_user_meta_data->>'utm_content', profiles.utm_content),
    utm_term = COALESCE(NEW.raw_user_meta_data->>'utm_term', profiles.utm_term),
    updated_at = now();
  
  RETURN NEW;
END;
$function$;

-- Добавляем поле has_paid_subscription в таблицу profiles
ALTER TABLE public.profiles 
ADD COLUMN IF NOT EXISTS has_paid_subscription BOOLEAN DEFAULT FALSE;

-- Обновляем существующих пользователей, у которых нет subscription_end_date
-- Устанавливаем им 5-дневный пробный период от даты создания
UPDATE public.profiles 
SET 
  subscription_end_date = created_at + INTERVAL '5 days',
  updated_at = NOW()
WHERE subscription_end_date IS NULL;

-- Обновляем функцию apply_promo_code для установки бонусных дней по умолчанию 5 вместо 15
CREATE OR REPLACE FUNCTION public.apply_promo_code(
  p_user_id uuid,
  p_promo_code text
)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
AS $function$
DECLARE
  v_promo_record RECORD;
  v_profile_record RECORD;
  v_new_end_date timestamp with time zone;
  v_bonus_days integer;
BEGIN
  -- Проверяем, что у пользователя есть оплаченная подписка
  SELECT * INTO v_profile_record
  FROM public.profiles
  WHERE id = p_user_id;
  
  IF NOT FOUND THEN
    RETURN jsonb_build_object(
      'success', false,
      'error', 'Профиль пользователя не найден'
    );
  END IF;
  
  -- Проверяем, что у пользователя есть оплаченная подписка
  IF NOT COALESCE(v_profile_record.has_paid_subscription, false) THEN
    RETURN jsonb_build_object(
      'success', false,
      'error', 'Промокод доступен только после оплаты ежемесячного тарифа'
    );
  END IF;
  
  -- Проверяем существование и валидность промокода
  SELECT * INTO v_promo_record
  FROM public.promo_codes
  WHERE code = p_promo_code
    AND is_active = true
    AND (expires_at IS NULL OR expires_at > NOW())
    AND (max_usage IS NULL OR usage_count < max_usage);
  
  IF NOT FOUND THEN
    RETURN jsonb_build_object(
      'success', false,
      'error', 'Промокод недействителен или истек'
    );
  END IF;
  
  -- Вычисляем новую дату окончания подписки
  v_bonus_days := COALESCE(v_promo_record.bonus_days, 5); -- Изменено с 15 на 5
  
  IF v_profile_record.subscription_end_date IS NULL OR v_profile_record.subscription_end_date < NOW() THEN
    -- Если подписка истекла или не установлена, начинаем от текущей даты
    v_new_end_date := NOW() + (v_bonus_days || ' days')::interval;
  ELSE
    -- Если подписка активна, добавляем дни к существующей дате
    v_new_end_date := v_profile_record.subscription_end_date + (v_bonus_days || ' days')::interval;
  END IF;
  
  -- Обновляем профиль пользователя
  UPDATE public.profiles
  SET 
    subscription_end_date = v_new_end_date,
    bonus_days = COALESCE(bonus_days, 0) + v_bonus_days,
    updated_at = NOW()
  WHERE id = p_user_id;
  
  -- Увеличиваем счетчик использования промокода
  UPDATE public.promo_codes
  SET 
    usage_count = usage_count + 1,
    updated_at = NOW()
  WHERE id = v_promo_record.id;
  
  -- Записываем конверсию (если есть партнер)
  IF v_promo_record.partner_id IS NOT NULL THEN
    INSERT INTO public.referral_conversions (
      partner_id,
      user_id,
      promo_code_id,
      conversion_type,
      amount,
      commission_earned
    ) VALUES (
      v_promo_record.partner_id,
      p_user_id,
      v_promo_record.id,
      'promo_code_usage',
      0,
      0
    );
  END IF;
  
  RETURN jsonb_build_object(
    'success', true,
    'bonus_days', v_bonus_days,
    'new_end_date', v_new_end_date,
    'message', 'Промокод успешно применен! Добавлено ' || v_bonus_days || ' дней к подписке.'
  );
END;
$function$;
