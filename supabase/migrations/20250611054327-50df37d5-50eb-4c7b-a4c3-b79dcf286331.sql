
-- Создаем таблицу для WhatsApp сессий
CREATE TABLE public.whatsapp_sessions (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users NOT NULL,
  session_name TEXT NOT NULL,
  qr_code TEXT,
  is_connected BOOLEAN NOT NULL DEFAULT false,
  last_activity TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Создаем таблицу для WhatsApp сообщений
CREATE TABLE public.whatsapp_messages (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  session_id UUID REFERENCES public.whatsapp_sessions NOT NULL,
  contact_phone TEXT NOT NULL,
  contact_name TEXT,
  message_text TEXT,
  message_type TEXT NOT NULL DEFAULT 'text',
  is_outgoing BOOLEAN NOT NULL DEFAULT false,
  timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  delivery_status TEXT DEFAULT 'sent',
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Создаем таблицу для WhatsApp контактов
CREATE TABLE public.whatsapp_contacts (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  session_id UUID REFERENCES public.whatsapp_sessions NOT NULL,
  phone TEXT NOT NULL,
  name TEXT,
  profile_pic_url TEXT,
  last_seen TIMESTAMP WITH TIME ZONE,
  is_blocked BOOLEAN DEFAULT false,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  UNIQUE(session_id, phone)
);

-- Включаем Row Level Security для всех таблиц
ALTER TABLE public.whatsapp_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.whatsapp_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.whatsapp_contacts ENABLE ROW LEVEL SECURITY;

-- Политики для whatsapp_sessions
CREATE POLICY "Users can view their own WhatsApp sessions" 
  ON public.whatsapp_sessions 
  FOR SELECT 
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own WhatsApp sessions" 
  ON public.whatsapp_sessions 
  FOR INSERT 
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own WhatsApp sessions" 
  ON public.whatsapp_sessions 
  FOR UPDATE 
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own WhatsApp sessions" 
  ON public.whatsapp_sessions 
  FOR DELETE 
  USING (auth.uid() = user_id);

-- Политики для whatsapp_messages
CREATE POLICY "Users can view messages from their sessions" 
  ON public.whatsapp_messages 
  FOR SELECT 
  USING (
    EXISTS (
      SELECT 1 FROM public.whatsapp_sessions 
      WHERE id = session_id AND user_id = auth.uid()
    )
  );

CREATE POLICY "Users can create messages in their sessions" 
  ON public.whatsapp_messages 
  FOR INSERT 
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.whatsapp_sessions 
      WHERE id = session_id AND user_id = auth.uid()
    )
  );

-- Политики для whatsapp_contacts
CREATE POLICY "Users can view contacts from their sessions" 
  ON public.whatsapp_contacts 
  FOR SELECT 
  USING (
    EXISTS (
      SELECT 1 FROM public.whatsapp_sessions 
      WHERE id = session_id AND user_id = auth.uid()
    )
  );

CREATE POLICY "Users can create contacts in their sessions" 
  ON public.whatsapp_contacts 
  FOR INSERT 
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.whatsapp_sessions 
      WHERE id = session_id AND user_id = auth.uid()
    )
  );

CREATE POLICY "Users can update contacts in their sessions" 
  ON public.whatsapp_contacts 
  FOR UPDATE 
  USING (
    EXISTS (
      SELECT 1 FROM public.whatsapp_sessions 
      WHERE id = session_id AND user_id = auth.uid()
    )
  );

-- Добавляем trigger для обновления updated_at
CREATE TRIGGER update_whatsapp_sessions_updated_at 
  BEFORE UPDATE ON public.whatsapp_sessions 
  FOR EACH ROW 
  EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_whatsapp_contacts_updated_at 
  BEFORE UPDATE ON public.whatsapp_contacts 
  FOR EACH ROW 
  EXECUTE FUNCTION public.update_updated_at_column();
