
-- Добавляем недостающее поле updated_at в таблицу promo_codes
ALTER TABLE public.promo_codes 
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Создаем триггер для автоматического обновления updated_at
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Применяем триггер к таблице promo_codes
DROP TRIGGER IF EXISTS update_promo_codes_updated_at ON public.promo_codes;
CREATE TRIGGER update_promo_codes_updated_at
    BEFORE UPDATE ON public.promo_codes
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();
