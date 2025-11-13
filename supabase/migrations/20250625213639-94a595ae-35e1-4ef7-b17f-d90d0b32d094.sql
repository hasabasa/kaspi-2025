
-- Создаем таблицу для подписок
CREATE TABLE public.subscriptions (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  UNIQUE(user_id)
);

-- Включаем RLS для безопасности
ALTER TABLE public.subscriptions ENABLE ROW LEVEL SECURITY;

-- Политика для админов - полный доступ
CREATE POLICY "Admins can manage all subscriptions" 
  ON public.subscriptions 
  FOR ALL 
  USING (public.has_role(auth.uid(), 'admin'));

-- Политика для пользователей - только чтение своих данных
CREATE POLICY "Users can view their own subscription" 
  ON public.subscriptions 
  FOR SELECT 
  USING (auth.uid() = user_id);

-- Добавляем триггер для автоматического обновления updated_at
CREATE TRIGGER update_subscriptions_updated_at
  BEFORE UPDATE ON public.subscriptions
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

-- Переносим данные из profiles в subscriptions
INSERT INTO public.subscriptions (user_id, expires_at)
SELECT id, COALESCE(subscription_end_date, now() + interval '5 days')
FROM public.profiles
WHERE id IS NOT NULL
ON CONFLICT (user_id) DO NOTHING;
