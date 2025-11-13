
-- Add phone column to profiles table if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'profiles' AND column_name = 'phone_verified') THEN
        ALTER TABLE public.profiles ADD COLUMN phone_verified BOOLEAN DEFAULT false;
    END IF;
END $$;

-- Update the handle_new_user function to handle phone registration
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  INSERT INTO public.profiles (id, full_name, company_name, phone, phone_verified)
  VALUES (
    NEW.id, 
    NEW.raw_user_meta_data->>'full_name', 
    NEW.raw_user_meta_data->>'company_name',
    COALESCE(NEW.phone, NEW.raw_user_meta_data->>'phone'),
    CASE WHEN NEW.phone IS NOT NULL THEN true ELSE false END
  );
  RETURN NEW;
END;
$$;
