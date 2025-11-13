
-- Исправляем создание администратора с обработкой конфликтов
DO $$
DECLARE
    admin_user_id uuid;
BEGIN
    -- Проверяем, существует ли пользователь admin@admin.com
    SELECT id INTO admin_user_id FROM auth.users WHERE email = 'admin@admin.com';
    
    -- Если пользователя нет, создаем его
    IF admin_user_id IS NULL THEN
        INSERT INTO auth.users (
            id,
            instance_id,
            email,
            encrypted_password,
            email_confirmed_at,
            created_at,
            updated_at,
            role,
            aud,
            confirmation_token,
            email_change_token_new,
            email_change_token_current,
            email_change,
            recovery_token,
            raw_app_meta_data,
            raw_user_meta_data,
            is_super_admin,
            last_sign_in_at
        ) VALUES (
            gen_random_uuid(),
            '00000000-0000-0000-0000-000000000000',
            'admin@admin.com',
            crypt('admin', gen_salt('bf')),
            NOW(),
            NOW(),
            NOW(),
            'authenticated',
            'authenticated',
            '',
            '',
            '',
            '',
            '',
            '{"provider": "email", "providers": ["email"]}',
            '{"full_name": "Администратор", "company_name": "Система"}',
            false,
            NOW()
        );
        
        -- Получаем ID только что созданного пользователя
        SELECT id INTO admin_user_id FROM auth.users WHERE email = 'admin@admin.com';
    ELSE
        -- Если пользователь существует, обновляем его данные с правильными значениями полей
        UPDATE auth.users SET
            encrypted_password = crypt('admin', gen_salt('bf')),
            email_change_token_new = '',
            email_change_token_current = '',
            email_change = '',
            recovery_token = '',
            confirmation_token = '',
            raw_app_meta_data = '{"provider": "email", "providers": ["email"]}',
            raw_user_meta_data = '{"full_name": "Администратор", "company_name": "Система"}',
            updated_at = NOW()
        WHERE id = admin_user_id;
    END IF;
    
    -- Создаем или обновляем профиль для администратора
    INSERT INTO public.profiles (
        id,
        full_name,
        company_name,
        phone,
        subscription_end_date,
        bonus_days,
        created_at,
        updated_at
    ) VALUES (
        admin_user_id,
        'Администратор',
        'Система',
        '+7700000000',
        NOW() + INTERVAL '365 days',
        0,
        NOW(),
        NOW()
    ) ON CONFLICT (id) DO UPDATE SET
        full_name = EXCLUDED.full_name,
        company_name = EXCLUDED.company_name,
        phone = EXCLUDED.phone,
        subscription_end_date = EXCLUDED.subscription_end_date,
        bonus_days = EXCLUDED.bonus_days,
        updated_at = NOW();
    
    -- Назначаем роль администратора (с обработкой конфликтов)
    INSERT INTO public.user_roles (
        user_id,
        role,
        created_at
    ) VALUES (
        admin_user_id,
        'admin'::app_role,
        NOW()
    ) ON CONFLICT (user_id, role) DO NOTHING;
    
END $$;
