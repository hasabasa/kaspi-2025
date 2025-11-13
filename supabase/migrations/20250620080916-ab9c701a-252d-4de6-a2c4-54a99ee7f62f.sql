
-- Обновляем функцию handle_new_user() для установки 3-дневного пробного периода
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
    bonus_days
  )
  VALUES (
    NEW.id, 
    NEW.raw_user_meta_data->>'full_name', 
    NEW.raw_user_meta_data->>'company_name',
    NEW.raw_user_meta_data->>'phone',
    NOW() + INTERVAL '3 days', -- 3-дневный пробный период
    0
  )
  ON CONFLICT (id) DO UPDATE SET
    full_name = COALESCE(NEW.raw_user_meta_data->>'full_name', profiles.full_name),
    company_name = COALESCE(NEW.raw_user_meta_data->>'company_name', profiles.company_name),
    phone = COALESCE(NEW.raw_user_meta_data->>'phone', profiles.phone),
    subscription_end_date = COALESCE(profiles.subscription_end_date, NOW() + INTERVAL '3 days'),
    updated_at = now();
  
  RETURN NEW;
END;
$function$;

-- Создаем функцию для применения промокода
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
  
  -- Получаем профиль пользователя
  SELECT * INTO v_profile_record
  FROM public.profiles
  WHERE id = p_user_id;
  
  IF NOT FOUND THEN
    RETURN jsonb_build_object(
      'success', false,
      'error', 'Профиль пользователя не найден'
    );
  END IF;
  
  -- Вычисляем новую дату окончания подписки
  v_bonus_days := COALESCE(v_promo_record.bonus_days, 15);
  
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
