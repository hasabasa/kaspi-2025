
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? '',
      { auth: { persistSession: false } }
    )

    const { email } = await req.json()

    if (!email) {
      return new Response(
        JSON.stringify({ success: false, error: 'Email обязателен' }),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' }, status: 400 }
      )
    }

    // Находим пользователя по email
    const { data: users } = await supabaseClient.auth.admin.listUsers()
    const user = users.users.find(u => u.email === email)

    if (!user) {
      return new Response(
        JSON.stringify({ success: false, error: 'Пользователь не найден' }),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' }, status: 404 }
      )
    }

    // Подтверждаем email
    const { error } = await supabaseClient.auth.admin.updateUserById(
      user.id,
      { 
        email_confirm: true,
        email_confirmed_at: new Date().toISOString()
      }
    )

    if (error) {
      console.error('Email confirmation error:', error)
      return new Response(
        JSON.stringify({ success: false, error: error.message }),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' }, status: 400 }
      )
    }

    return new Response(
      JSON.stringify({ 
        success: true, 
        message: `Email ${email} успешно подтвержден` 
      }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  } catch (error) {
    console.error('Function error:', error)
    return new Response(
      JSON.stringify({ success: false, error: error.message }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' }, status: 500 }
    )
  }
})
