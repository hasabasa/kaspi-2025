
-- Удаляем ВСЕ существующие политики для profiles
DROP POLICY IF EXISTS "Admins can view all profiles" ON public.profiles;
DROP POLICY IF EXISTS "Users can view own profile" ON public.profiles;
DROP POLICY IF EXISTS "Users can insert own profile" ON public.profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON public.profiles;

-- Удаляем ВСЕ существующие политики для user_roles
DROP POLICY IF EXISTS "Admins can view all user roles" ON public.user_roles;
DROP POLICY IF EXISTS "Users can view own roles" ON public.user_roles;

-- Создаем функцию для проверки роли пользователя с SECURITY DEFINER
CREATE OR REPLACE FUNCTION public.is_admin(user_id uuid DEFAULT auth.uid())
RETURNS boolean
LANGUAGE sql
SECURITY DEFINER
STABLE
AS $$
  SELECT EXISTS (
    SELECT 1 
    FROM public.user_roles 
    WHERE user_roles.user_id = is_admin.user_id 
    AND role = 'admin'
  );
$$;

-- Создаем новые политики для profiles
CREATE POLICY "Admins can view all profiles" 
  ON public.profiles 
  FOR SELECT 
  USING (public.is_admin());

CREATE POLICY "Users can view own profile" 
  ON public.profiles 
  FOR SELECT 
  USING (auth.uid() = id OR public.is_admin());

CREATE POLICY "Users can update own profile" 
  ON public.profiles 
  FOR UPDATE 
  USING (auth.uid() = id OR public.is_admin());

-- Создаем новые политики для user_roles
CREATE POLICY "Admins can view all user roles" 
  ON public.user_roles 
  FOR SELECT 
  USING (public.is_admin());

CREATE POLICY "Users can view own roles" 
  ON public.user_roles 
  FOR SELECT 
  USING (auth.uid() = user_id OR public.is_admin());

-- Разрешаем админам управлять ролями
CREATE POLICY "Admins can insert user roles" 
  ON public.user_roles 
  FOR INSERT 
  WITH CHECK (public.is_admin());

CREATE POLICY "Admins can delete user roles" 
  ON public.user_roles 
  FOR DELETE 
  USING (public.is_admin());

-- Разрешаем админам обновлять профили
CREATE POLICY "Admins can update all profiles" 
  ON public.profiles 
  FOR UPDATE 
  USING (public.is_admin());
