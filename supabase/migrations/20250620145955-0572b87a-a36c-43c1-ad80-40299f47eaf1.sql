
-- Добавляем функцию для создания промокода партнером
CREATE OR REPLACE FUNCTION public.create_partner_promo_code(
  p_partner_id UUID,
  p_code TEXT,
  p_bonus_days INTEGER DEFAULT 15,
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
  
  -- Создаем промокод (неактивный по умолчанию)
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
    'message', 'Промокод создан. Активируйте его для использования.'
  );
END;
$$;

-- Добавляем функцию для активации промокода
CREATE OR REPLACE FUNCTION public.activate_promo_code(
  p_promo_id UUID,
  p_partner_id UUID
)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  -- Проверяем, что промокод принадлежит партнеру
  IF NOT EXISTS (
    SELECT 1 FROM public.promo_codes 
    WHERE id = p_promo_id 
    AND partner_id = p_partner_id
  ) THEN
    RETURN jsonb_build_object(
      'success', false,
      'error', 'Промокод не найден'
    );
  END IF;
  
  -- Активируем промокод
  UPDATE public.promo_codes
  SET 
    is_active = true,
    updated_at = NOW()
  WHERE id = p_promo_id;
  
  RETURN jsonb_build_object(
    'success', true,
    'message', 'Промокод успешно активирован'
  );
END;
$$;

-- Обновляем RLS политики для promo_codes
DROP POLICY IF EXISTS "Partners can view own promo codes" ON public.promo_codes;
DROP POLICY IF EXISTS "Only admins can manage promo codes" ON public.promo_codes;

-- Партнеры могут просматривать свои промокоды
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

-- Партнеры могут создавать свои промокоды через функцию
CREATE POLICY "Partners can create promo codes via function" 
  ON public.promo_codes 
  FOR INSERT 
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.partners 
      WHERE id = promo_codes.partner_id 
      AND user_id = auth.uid()
    ) OR public.has_role(auth.uid(), 'admin')
  );

-- Партнеры могут обновлять свои промокоды
CREATE POLICY "Partners can update own promo codes" 
  ON public.promo_codes 
  FOR UPDATE 
  USING (
    EXISTS (
      SELECT 1 FROM public.partners 
      WHERE id = promo_codes.partner_id 
      AND user_id = auth.uid()
    ) OR public.has_role(auth.uid(), 'admin')
  );

-- Админы могут все
CREATE POLICY "Admins can manage all promo codes" 
  ON public.promo_codes 
  FOR ALL 
  USING (public.has_role(auth.uid(), 'admin'));
