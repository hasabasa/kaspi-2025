
-- Подтверждаем email для всех существующих партнеров с доменом @partners.internal
UPDATE auth.users 
SET email_confirmed_at = COALESCE(email_confirmed_at, now())
WHERE email LIKE '%@partners.internal' 
  AND email_confirmed_at IS NULL;

-- Также подтверждаем для всех пользователей, у которых есть роль партнера
UPDATE auth.users 
SET email_confirmed_at = COALESCE(email_confirmed_at, now())
WHERE id IN (
  SELECT DISTINCT user_id 
  FROM public.user_roles 
  WHERE role = 'partner'
) AND email_confirmed_at IS NULL;
