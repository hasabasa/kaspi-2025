
-- Создаем администратора с данными admin/admin
-- Сначала проверяем, есть ли уже пользователь с таким email
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
            recovery_token,
            raw_app_meta_data,
            raw_user_meta_data,
            is_super_admin,
            last_sign_in_at
        ) VALUES (
            gen_random_uuid(),
            '00000000-0000-0000-0000-000000000000',
            'admin@admin.com',
            crypt('admin', gen_salt('bf')), -- Хеш пароля "admin"
            NOW(),
            NOW(),
            NOW(),
            'authenticated',
            'authenticated',
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
        NOW() + INTERVAL '365 days', -- Долгосрочная подписка для админа
        0,
        NOW(),
        NOW()
    ) ON CONFLICT (id) DO UPDATE SET
        full_name = EXCLUDED.full_name,
        company_name = EXCLUDED.company_name,
        subscription_end_date = EXCLUDED.subscription_end_date,
        updated_at = NOW();
    
    -- Назначаем роль администратора
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
