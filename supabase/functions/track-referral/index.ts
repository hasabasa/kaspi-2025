
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  console.log('track-referral function called with method:', req.method)
  
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? '',
      { auth: { persistSession: false } }
    )

    // Parse request body for POST requests
    let requestData;
    if (req.method === 'POST') {
      requestData = await req.json();
      console.log('Request body data:', requestData);
    } else {
      // Fallback to URL params for GET requests (backwards compatibility)
      const url = new URL(req.url);
      requestData = {
        partner_code: url.searchParams.get('ref') || url.searchParams.get('partner'),
        utm_source: url.searchParams.get('utm_source'),
        utm_medium: url.searchParams.get('utm_medium'),
        utm_campaign: url.searchParams.get('utm_campaign'),
        utm_content: url.searchParams.get('utm_content'),
        utm_term: url.searchParams.get('utm_term'),
        url: url.searchParams.get('url') || req.url
      };
    }

    const { partner_code, utm_source, utm_medium, utm_campaign, utm_content, utm_term, url } = requestData;
    
    console.log('Tracking referral click:', { partner_code, utm_source, utm_medium, utm_campaign, url })

    if (!partner_code) {
      console.log('No partner code provided')
      return new Response(
        JSON.stringify({ success: false, error: 'No partner code provided' }),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' }, status: 400 }
      )
    }

    // Find partner by code
    const { data: partner, error: partnerError } = await supabaseClient
      .from('partners')
      .select('id, partner_code, is_active')
      .eq('partner_code', partner_code)
      .eq('is_active', true)
      .single()

    if (partnerError || !partner) {
      console.error('Partner not found:', partnerError)
      return new Response(
        JSON.stringify({ success: false, error: 'Partner not found or inactive' }),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' }, status: 404 }
      )
    }

    console.log('Found partner:', partner.id, partner.partner_code)

    // Get visitor information
    const userAgent = req.headers.get('user-agent')
    const referrer = req.headers.get('referer')
    const forwardedFor = req.headers.get('x-forwarded-for')
    const realIp = req.headers.get('x-real-ip')
    const visitorIp = forwardedFor?.split(',')[0] || realIp || 'unknown'

    console.log('Visitor info:', { visitorIp, userAgent, referrer })

    // Record click
    const { data: clickData, error: clickError } = await supabaseClient
      .from('referral_clicks')
      .insert({
        partner_id: partner.id,
        visitor_ip: visitorIp,
        user_agent: userAgent,
        referrer: referrer,
        utm_source: utm_source,
        utm_medium: utm_medium,
        utm_campaign: utm_campaign,
        utm_content: utm_content,
        utm_term: utm_term,
        page_url: url || req.url
      })
      .select()
      .single()

    if (clickError) {
      console.error('Error recording click:', clickError)
      return new Response(
        JSON.stringify({ success: false, error: 'Failed to record click' }),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' }, status: 500 }
      )
    }

    console.log('Click recorded successfully:', clickData.id)

    return new Response(
      JSON.stringify({ 
        success: true, 
        clickId: clickData.id,
        partnerId: partner.id,
        message: 'Click tracked successfully' 
      }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' }, status: 200 }
    )

  } catch (error) {
    console.error('Function error:', error)
    return new Response(
      JSON.stringify({ success: false, error: error.message }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' }, status: 500 }
    )
  }
})
