
-- Add missing columns to existing profiles table if they don't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'profiles' AND column_name = 'phone') THEN
        ALTER TABLE public.profiles ADD COLUMN phone TEXT;
    END IF;
END $$;

-- Enable RLS on kaspi_stores table if not already enabled
ALTER TABLE public.kaspi_stores ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist and recreate them
DROP POLICY IF EXISTS "Users can view own stores" ON public.kaspi_stores;
DROP POLICY IF EXISTS "Users can insert own stores" ON public.kaspi_stores;
DROP POLICY IF EXISTS "Users can update own stores" ON public.kaspi_stores;
DROP POLICY IF EXISTS "Users can delete own stores" ON public.kaspi_stores;

-- Create RLS policies for kaspi_stores table
CREATE POLICY "Users can view own stores" 
  ON public.kaspi_stores 
  FOR SELECT 
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own stores" 
  ON public.kaspi_stores 
  FOR INSERT 
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own stores" 
  ON public.kaspi_stores 
  FOR UPDATE 
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own stores" 
  ON public.kaspi_stores 
  FOR DELETE 
  USING (auth.uid() = user_id);
