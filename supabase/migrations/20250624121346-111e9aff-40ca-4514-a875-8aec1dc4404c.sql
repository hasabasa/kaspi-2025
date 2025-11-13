
-- Проверяем, есть ли пользователи в auth.users без соответствующих записей в profiles
-- и создаем для них профили

INSERT INTO public.profiles (
    id,
    full_name,
    company_name,
    phone,
    subscription_end_date,
    bonus_days,
    created_at,
    updated_at
)
SELECT 
    au.id,
    au.raw_user_meta_data->>'full_name',
    au.raw_user_meta_data->>'company_name',
    au.raw_user_meta_data->>'phone',
    COALESCE(
        (au.raw_user_meta_data->>'subscription_end_date')::timestamp with time zone,
        au.created_at + INTERVAL '3 days'
    ),
    COALESCE((au.raw_user_meta_data->>'bonus_days')::integer, 0),
    au.created_at,
    au.updated_at
FROM auth.users au
LEFT JOIN public.profiles p ON p.id = au.id
WHERE p.id IS NULL
ON CONFLICT (id) DO NOTHING;

-- Создаем политики RLS для админов, чтобы они могли видеть всех пользователей
DROP POLICY IF EXISTS "Admins can view all profiles" ON public.profiles;
CREATE POLICY "Admins can view all profiles" 
  ON public.profiles 
  FOR SELECT 
  USING (
    auth.uid() IN (
      SELECT user_id 
      FROM public.user_roles 
      WHERE role = 'admin'
    )
  );

-- Аналогично для user_roles
DROP POLICY IF EXISTS "Admins can view all user roles" ON public.user_roles;
CREATE POLICY "Admins can view all user roles" 
  ON public.user_roles 
  FOR SELECT 
  USING (
    auth.uid() IN (
      SELECT user_id 
      FROM public.user_roles 
      WHERE role = 'admin'
    )
  );
