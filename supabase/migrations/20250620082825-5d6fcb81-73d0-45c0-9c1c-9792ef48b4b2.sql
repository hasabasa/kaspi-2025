
-- Обновляем существующих пользователей, у которых нет subscription_end_date
-- Устанавливаем им 3-дневный пробный период от даты создания
UPDATE public.profiles 
SET 
  subscription_end_date = created_at + INTERVAL '3 days',
  updated_at = NOW()
WHERE subscription_end_date IS NULL;
