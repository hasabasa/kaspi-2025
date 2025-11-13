
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

// Заголовки CORS для обеспечения доступа из веб-приложения
const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

// Обработчик для разрешения запросов CORS preflight
const handleCorsRequest = () => {
  return new Response(null, {
    headers: corsHeaders,
    status: 204,
  });
};

serve(async (req) => {
  // Обработка CORS preflight запросов
  if (req.method === "OPTIONS") {
    return handleCorsRequest();
  }

  try {
    // Создаем клиент Supabase с помощью переменных окружения
    const supabaseUrl = Deno.env.get("SUPABASE_URL") || "";
    const supabaseKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") || "";
    const supabase = createClient(supabaseUrl, supabaseKey);

    // Создаем анонимный клиент для проверки JWT
    const authHeader = req.headers.get("Authorization") || "";
    if (!authHeader) {
      return new Response(
        JSON.stringify({ error: "Missing Authorization header" }),
        {
          status: 401,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        }
      );
    }

    // Получаем данные из тела запроса
    const requestData = await req.json();
    const { category, userId } = requestData;

    if (!category) {
      return new Response(
        JSON.stringify({ error: "Category is required" }),
        {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        }
      );
    }

    // В реальном приложении здесь был бы код для поиска ниш в API Kaspi
    // по указанной категории

    // Имитируем поиск ниш (возвращаем случайные данные)
    const mockNiches = [];
    for (let i = 0; i < 10; i++) {
      const soldQuantity = Math.floor(Math.random() * 500) + 50;
      const price = Math.floor(Math.random() * 50000) + 5000;
      
      // Генерируем данные графика продаж за 6 месяцев
      const chartData = [];
      for (let j = 0; j < 6; j++) {
        const date = new Date();
        date.setMonth(date.getMonth() - (5 - j));
        
        chartData.push({
          month: date.toLocaleString('default', { month: 'short' }),
          sales: Math.floor(Math.random() * 500) + 50
        });
      }
      
      mockNiches.push({
        id: `NICHE${i}`,
        name: `Товар в нише ${category} #${i + 1}`,
        category: category,
        price: price,
        soldQuantity: soldQuantity,
        revenue: price * soldQuantity,
        rating: (Math.random() * 2 + 3).toFixed(1),
        sellers: Math.floor(Math.random() * 20) + 1,
        chartData: chartData
      });
    }

    // Сортируем ниши по выручке (от большей к меньшей)
    mockNiches.sort((a, b) => b.revenue - a.revenue);

    // Возвращаем результат
    return new Response(
      JSON.stringify({ 
        success: true, 
        data: mockNiches
      }),
      {
        status: 200,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      }
    );
  } catch (error) {
    console.error("Error processing request:", error);
    return new Response(
      JSON.stringify({ error: "Internal Server Error" }),
      {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      }
    );
  }
});
