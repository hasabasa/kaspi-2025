
-- Создаем функцию для удаления пользователя (только для админов)
CREATE OR REPLACE FUNCTION public.delete_user_account(target_user_id uuid)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  -- Проверяем, что текущий пользователь является админом
  IF NOT public.has_role(auth.uid(), 'admin') THEN
    RETURN jsonb_build_object(
      'success', false,
      'error', 'Недостаточно прав доступа'
    );
  END IF;
  
  -- Проверяем, что пользователь существует
  IF NOT EXISTS (SELECT 1 FROM auth.users WHERE id = target_user_id) THEN
    RETURN jsonb_build_object(
      'success', false,
      'error', 'Пользователь не найден'
    );
  END IF;
  
  -- Не позволяем удалить самого себя
  IF target_user_id = auth.uid() THEN
    RETURN jsonb_build_object(
      'success', false,
      'error', 'Нельзя удалить свой собственный аккаунт'
    );
  END IF;
  
  -- Удаляем связанные данные из публичных таблиц (каскадные связи должны сработать автоматически)
  -- Удаляем профиль пользователя
  DELETE FROM public.profiles WHERE id = target_user_id;
  
  -- Удаляем роли пользователя
  DELETE FROM public.user_roles WHERE user_id = target_user_id;
  
  -- Если пользователь является партнером, удаляем связанные данные
  DELETE FROM public.partners WHERE user_id = target_user_id;
  
  -- Удаляем пользователя из auth.users (это должно быть последним)
  DELETE FROM auth.users WHERE id = target_user_id;
  
  RETURN jsonb_build_object(
    'success', true,
    'message', 'Пользователь успешно удален'
  );
END;
$$;
