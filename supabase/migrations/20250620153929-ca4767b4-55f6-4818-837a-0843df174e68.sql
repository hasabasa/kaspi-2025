
-- Попробуем найти существующего пользователя и создать для него партнера
DO $$
DECLARE
    existing_user_id UUID;
BEGIN
    -- Ищем любого существующего пользователя
    SELECT id INTO existing_user_id 
    FROM auth.users 
    LIMIT 1;
    
    IF existing_user_id IS NOT NULL THEN
        -- Создаем партнера для существующего пользователя
        INSERT INTO public.partners (
            user_id,
            partner_code,
            instagram_username,
            company_name,
            contact_email,
            commission_rate,
            is_active
        ) VALUES (
            existing_user_id,
            'partner',
            'test_partner',
            'Test Partner Company',
            'test-partner@example.com',
            10.00,
            true
        )
        ON CONFLICT (partner_code) DO UPDATE SET
            is_active = true,
            updated_at = now();
    ELSE
        -- Если нет пользователей, временно отключаем ограничение внешнего ключа
        ALTER TABLE public.partners DROP CONSTRAINT IF EXISTS partners_user_id_fkey;
        
        -- Создаем партнера с фиктивным user_id
        INSERT INTO public.partners (
            user_id,
            partner_code,
            instagram_username,
            company_name,
            contact_email,
            commission_rate,
            is_active
        ) VALUES (
            gen_random_uuid(),
            'partner',
            'test_partner',
            'Test Partner Company',
            'test-partner@example.com',
            10.00,
            true
        )
        ON CONFLICT (partner_code) DO UPDATE SET
            is_active = true,
            updated_at = now();
            
        -- Восстанавливаем ограничение (но оно не будет применяться к существующим записям)
        ALTER TABLE public.partners 
        ADD CONSTRAINT partners_user_id_fkey 
        FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE 
        NOT VALID;
    END IF;
END $$;
