
-- ПОЛНОЕ ИСПРАВЛЕНИЕ БАЗЫ ДАННЫХ ДЛЯ АУТЕНТИФИКАЦИИ
-- Выполняем все исправления в правильном порядке

-- 1. Удаляем все существующие политики RLS для profiles
DROP POLICY IF EXISTS "Users can view own profile" ON public.profiles;
DROP POLICY IF EXISTS "Users can insert own profile" ON public.profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON public.profiles;
DROP POLICY IF EXISTS "Allow profile creation" ON public.profiles;
DROP POLICY IF EXISTS "Enable insert for authenticated users only" ON public.profiles;
DROP POLICY IF EXISTS "Enable read access for all users" ON public.profiles;
DROP POLICY IF EXISTS "Enable update for users based on email" ON public.profiles;

-- 2. Удаляем существующий триггер если есть
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

-- 3. Удаляем и пересоздаем функцию handle_new_user с правильными правами
DROP FUNCTION IF EXISTS public.handle_new_user();

CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  INSERT INTO public.profiles (id, full_name, company_name, phone)
  VALUES (
    NEW.id, 
    NEW.raw_user_meta_data->>'full_name', 
    NEW.raw_user_meta_data->>'company_name',
    NEW.raw_user_meta_data->>'phone'
  );
  RETURN NEW;
END;
$$;

-- 4. СОЗДАЕМ ТРИГГЕР (это самое важное!)
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- 5. Убеждаемся что RLS включен
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- 6. Создаем правильные RLS политики
-- Политика для SELECT - пользователи видят только свои профили
CREATE POLICY "Users can view own profile" 
  ON public.profiles 
  FOR SELECT 
  USING (auth.uid() = id);

-- Политика для INSERT - разрешаем системные вставки через триггер
CREATE POLICY "Allow profile creation" 
  ON public.profiles 
  FOR INSERT 
  WITH CHECK (true);

-- Политика для UPDATE - пользователи могут обновлять только свои профили
CREATE POLICY "Users can update own profile" 
  ON public.profiles 
  FOR UPDATE 
  USING (auth.uid() = id);

-- 7. Предоставляем необходимые права функции
GRANT USAGE ON SCHEMA public TO supabase_auth_admin;
GRANT INSERT ON public.profiles TO supabase_auth_admin;

-- 8. Очищаем пользователей без профилей чтобы избежать конфликтов
-- (Опционально - раскомментируйте если нужно)
-- DELETE FROM auth.users WHERE id NOT IN (SELECT id FROM public.profiles);
