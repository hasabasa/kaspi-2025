
-- Обновляем функцию создания промокода партнером
CREATE OR REPLACE FUNCTION public.create_partner_promo_code(
  p_partner_id UUID,
  p_code TEXT,
  p_bonus_days INTEGER DEFAULT 10,
  p_max_usage INTEGER DEFAULT NULL,
  p_expires_at TIMESTAMP WITH TIME ZONE DEFAULT NULL
)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_promo_id UUID;
BEGIN
  -- Проверяем, что партнер существует
  IF NOT EXISTS (SELECT 1 FROM public.partners WHERE id = p_partner_id AND is_active = true) THEN
    RETURN jsonb_build_object(
      'success', false,
      'error', 'Партнер не найден или неактивен'
    );
  END IF;
  
  -- Проверяем, что промокод не существует
  IF EXISTS (SELECT 1 FROM public.promo_codes WHERE code = UPPER(p_code)) THEN
    RETURN jsonb_build_object(
      'success', false,
      'error', 'Промокод уже существует'
    );
  END IF;
  
  -- Отключаем все старые активные промокоды этого партнера
  UPDATE public.promo_codes
  SET 
    is_active = false,
    updated_at = NOW()
  WHERE partner_id = p_partner_id AND is_active = true;
  
  -- Создаем новый промокод (неактивный по умолчанию)
  INSERT INTO public.promo_codes (
    partner_id,
    code,
    bonus_days,
    max_usage,
    expires_at,
    is_active
  ) VALUES (
    p_partner_id,
    UPPER(p_code),
    p_bonus_days,
    p_max_usage,
    p_expires_at,
    false  -- создаем неактивным
  ) RETURNING id INTO v_promo_id;
  
  RETURN jsonb_build_object(
    'success', true,
    'promo_id', v_promo_id,
    'message', 'Промокод создан. Старые промокоды отключены. Активируйте новый для использования.'
  );
END;
$$;

-- Обновляем функцию применения промокода (изменяем значение по умолчанию с 15 на 10)
CREATE OR REPLACE FUNCTION public.apply_promo_code(p_user_id uuid, p_promo_code text)
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
  v_bonus_days := COALESCE(v_promo_record.bonus_days, 10);
  
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
