
-- Исправляем триггер для создания профилей пользователей
-- Сначала удаляем все существующие триггеры и функции
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
DROP TRIGGER IF EXISTS create_profile_on_signup ON auth.users;
DROP FUNCTION IF EXISTS public.handle_new_user() CASCADE;
DROP FUNCTION IF EXISTS public.create_profile_for_new_user() CASCADE;

-- Создаем новую функцию с правильной обработкой конфликтов
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER
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
  )
  ON CONFLICT (id) DO UPDATE SET
    full_name = COALESCE(NEW.raw_user_meta_data->>'full_name', profiles.full_name),
    company_name = COALESCE(NEW.raw_user_meta_data->>'company_name', profiles.company_name),
    phone = COALESCE(NEW.raw_user_meta_data->>'phone', profiles.phone),
    updated_at = now();
  
  RETURN NEW;
END;
$$;

-- Создаем новый триггер
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
