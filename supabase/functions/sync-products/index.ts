
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
    const { storeId } = requestData;

    if (!storeId) {
      return new Response(
        JSON.stringify({ error: "Store ID is required" }),
        {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        }
      );
    }

    // Получаем информацию о магазине
    const { data: storeData, error: storeError } = await supabase
      .from("kaspi_stores")
      .select("*")
      .eq("id", storeId)
      .single();

    if (storeError || !storeData) {
      console.error("Error fetching store:", storeError);
      return new Response(
        JSON.stringify({ error: "Store not found" }),
        {
          status: 404,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        }
      );
    }

    // В реальном приложении здесь был бы код для интеграции с API Kaspi
    // и импорта товаров в базу данных

    // Имитируем синхронизацию товаров (для примера добавляем 5 тестовых товаров)
    const mockProducts = [];
    const categories = ["Электроника", "Бытовая техника", "Мебель", "Одежда", "Спорт"];
    
    for (let i = 0; i < 5; i++) {
        mockProducts.push{
        store_id: storeId,
        name: `Тестовый товар ${i + 1}`,
        price: Math.floor(Math.random() * 50000) + 5000,
        kaspi_product_id: `KP${Math.floor(Math.random() * 1000000)}`,
        image_url: `https://picsum.photos/200/300?random=${i}`,
        category: categories[Math.floor(Math.random() * categories.length)],
        bot_active: false
      };
    }

    // Сохраняем товары в базе данных
    const { data: insertedProducts, error: insertError } = await supabase
      .from("products")
      .insert(mockProducts)
      .select();

    if (insertError) {
      console.error("Error inserting products:", insertError);
      return new Response(
        JSON.stringify({ error: "Failed to insert products" }),
        {
          status: 500,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        }
      );
    }

    // Обновляем счетчик товаров в магазине
    const { error: updateError } = await supabase
      .from("kaspi_stores")
      .update({ 
        products_count: storeData.products_count + mockProducts.length,
        last_sync: new Date().toISOString()
      })
      .eq("id", storeId);

    if (updateError) {
      console.error("Error updating store:", updateError);
    }

    // Возвращаем результат
    return new Response(
      JSON.stringify({ 
        success: true, 
        message: `Synchronized ${mockProducts.length} products`,
        products: insertedProducts
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
