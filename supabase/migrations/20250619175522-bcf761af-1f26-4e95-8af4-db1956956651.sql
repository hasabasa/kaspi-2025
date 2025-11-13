
-- Fix RLS policies for profiles table to allow trigger to work
-- First, enable RLS if not already enabled
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can view own profile" ON public.profiles;
DROP POLICY IF EXISTS "Users can insert own profile" ON public.profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON public.profiles;

-- Create new policies that work with the trigger
-- Allow SELECT for authenticated users to view their own profile
CREATE POLICY "Users can view own profile" 
  ON public.profiles 
  FOR SELECT 
  USING (auth.uid() = id);

-- Allow INSERT for the trigger function (no restrictions for system inserts)
CREATE POLICY "Allow profile creation" 
  ON public.profiles 
  FOR INSERT 
  WITH CHECK (true);

-- Allow UPDATE for authenticated users to update their own profile
CREATE POLICY "Users can update own profile" 
  ON public.profiles 
  FOR UPDATE 
  USING (auth.uid() = id);
