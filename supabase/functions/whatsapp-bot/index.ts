
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

interface WhatsAppMessage {
  id: string;
  from: string;
  to: string;
  body: string;
  type: string;
  timestamp: number;
  fromMe: boolean;
}

interface WhatsAppContact {
  id: string;
  name: string;
  pushname: string;
  profilePicUrl?: string;
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_ANON_KEY') ?? '',
      {
        global: {
          headers: { Authorization: req.headers.get('Authorization')! },
        },
      }
    )

    const {
      data: { user },
    } = await supabaseClient.auth.getUser()

    if (!user) {
      return new Response('Unauthorized', { status: 401, headers: corsHeaders })
    }

    const { method } = req
    const url = new URL(req.url)
    const action = url.searchParams.get('action')

    switch (action) {
      case 'create_session':
        return await createSession(supabaseClient, user.id)
      
      case 'get_qr':
        const sessionId = url.searchParams.get('session_id')
        return await getQRCode(supabaseClient, sessionId!)
      
      case 'send_message':
        const { session_id, phone, message } = await req.json()
        return await sendMessage(supabaseClient, session_id, phone, message)
      
      case 'get_messages':
        const messagesSessionId = url.searchParams.get('session_id')
        return await getMessages(supabaseClient, messagesSessionId!)
      
      case 'get_contacts':
        const contactsSessionId = url.searchParams.get('session_id')
        return await getContacts(supabaseClient, contactsSessionId!)
      
      default:
        return new Response('Invalid action', { status: 400, headers: corsHeaders })
    }
  } catch (error) {
    console.error('Error:', error)
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    })
  }
})

async function createSession(supabaseClient: any, userId: string) {
  const sessionName = `session_${Date.now()}`
  
  const { data: session, error } = await supabaseClient
    .from('whatsapp_sessions')
    .insert({
      user_id: userId,
      session_name: sessionName,
      is_connected: false
    })
    .select()
    .single()

  if (error) {
    throw new Error(`Failed to create session: ${error.message}`)
  }

  // Генерируем QR код (симуляция)
  const qrCode = generateQRCode()
  
  await supabaseClient
    .from('whatsapp_sessions')
    .update({ qr_code: qrCode })
    .eq('id', session.id)

  return new Response(JSON.stringify({ 
    session_id: session.id,
    qr_code: qrCode,
    status: 'waiting_for_scan'
  }), {
    headers: { ...corsHeaders, 'Content-Type': 'application/json' },
  })
}

async function getQRCode(supabaseClient: any, sessionId: string) {
  const { data: session } = await supabaseClient
    .from('whatsapp_sessions')
    .select('qr_code, is_connected')
    .eq('id', sessionId)
    .single()

  if (!session) {
    return new Response('Session not found', { status: 404, headers: corsHeaders })
  }

  return new Response(JSON.stringify({
    qr_code: session.qr_code,
    is_connected: session.is_connected
  }), {
    headers: { ...corsHeaders, 'Content-Type': 'application/json' },
  })
}

async function sendMessage(supabaseClient: any, sessionId: string, phone: string, message: string) {
  // Симуляция отправки сообщения
  const messageId = `msg_${Date.now()}`
  
  const { error } = await supabaseClient
    .from('whatsapp_messages')
    .insert({
      session_id: sessionId,
      contact_phone: phone,
      message_text: message,
      message_type: 'text',
      is_outgoing: true,
      delivery_status: 'sent'
    })

  if (error) {
    throw new Error(`Failed to save message: ${error.message}`)
  }

  return new Response(JSON.stringify({
    message_id: messageId,
    status: 'sent'
  }), {
    headers: { ...corsHeaders, 'Content-Type': 'application/json' },
  })
}

async function getMessages(supabaseClient: any, sessionId: string) {
  const { data: messages, error } = await supabaseClient
    .from('whatsapp_messages')
    .select('*')
    .eq('session_id', sessionId)
    .order('timestamp', { ascending: true })

  if (error) {
    throw new Error(`Failed to get messages: ${error.message}`)
  }

  return new Response(JSON.stringify({ messages }), {
    headers: { ...corsHeaders, 'Content-Type': 'application/json' },
  })
}

async function getContacts(supabaseClient: any, sessionId: string) {
  const { data: contacts, error } = await supabaseClient
    .from('whatsapp_contacts')
    .select('*')
    .eq('session_id', sessionId)
    .order('name')

  if (error) {
    throw new Error(`Failed to get contacts: ${error.message}`)
  }

  return new Response(JSON.stringify({ contacts }), {
    headers: { ...corsHeaders, 'Content-Type': 'application/json' },
  })
}

function generateQRCode(): string {
  // Генерируем симуляцию QR кода
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='
  let result = ''
  for (let i = 0; i < 200; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  return result
}
