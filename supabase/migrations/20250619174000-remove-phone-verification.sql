
-- Remove phone_verified column from profiles table
ALTER TABLE public.profiles DROP COLUMN IF EXISTS phone_verified;

-- Update the handle_new_user function to handle phone as mandatory field
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
