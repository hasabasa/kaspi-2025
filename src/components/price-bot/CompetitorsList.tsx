
import { useState, useEffect } from "react";
import { ArrowDown, ArrowUp } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { motion } from "framer-motion";
import { toast } from "sonner";
import { supabase } from "@/integrations/supabase/client";
import { Competitor } from "@/types";

interface CompetitorsListProps {
  productId: string;
}

const CompetitorsList = ({ productId }: CompetitorsListProps) => {
  const [competitors, setCompetitors] = useState<Competitor[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // Загрузка конкурентов при изменении выбранного товара
    const loadCompetitors = async () => {
      setIsLoading(true);
      try {
        // Загружаем конкурентов из Supabase
        const { data, error } = await supabase
          .from('competitors')
          .select('*')
          .eq('product_id', productId);
        
        if (error) throw error;
        
        // Используем приведение типов для правильной работы с данными из Supabase
        setCompetitors(data as Competitor[] || []);
      } catch (error) {
        console.error("Error loading competitors:", error);
        toast.error("Ошибка при загрузке конкурентов");
      } finally {
        setIsLoading(false);
      }
    };
    
    if (productId) {
      loadCompetitors();
    }
  }, [productId]);

  const handleSetPrice = async (competitorId: string) => {
    const competitor = competitors.find(c => c.id === competitorId);
    if (!competitor) return;
    
    try {
      // Получаем текущие данные о продукте
      const { data: product, error: productError } = await supabase
        .from('products')
        .select('*')
        .eq('id', productId)
        .single();
      
      if (productError) throw productError;
      
      // Устанавливаем цену на 1 тенге ниже, чем у конкурента
      const newPrice = Number(competitor.price) - 1;
      
      // Проверяем минимальную прибыльность
      // В реальном приложении здесь будет проверка себестоимости и минимальной прибыли
      
      // Обновляем цену в БД
      const { error } = await supabase
        .from('products')
        .update({
          price: newPrice,
          updated_at: new Date().toISOString()
        })
        .eq('id', productId);
        
      if (error) throw error;
      
      toast.success(`Цена обновлена до ${newPrice.toLocaleString()} ₸`);
      
      // Обновляем UI
      const updatedCompetitors = competitors.map(c => {
        if (c.id === competitor.id) {
          return { ...c, price_change: -1 };
        }
        return c;
      });
      setCompetitors(updatedCompetitors);
    } catch (error: any) {
      console.error("Error updating price:", error);
      toast.error(error.message || "Ошибка при обновлении цены");
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 gap-4">
        {competitors.length > 0 ? (
          competitors.map((competitor) => (
            <motion.div
              key={competitor.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white rounded-xl p-4 shadow-sm border"
            >
              <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h3 className="font-medium">{competitor.name}</h3>
                    <Badge variant="secondary">{(competitor.rating || 0).toFixed(1)} ★</Badge>
                  </div>
                  <div className="text-sm text-gray-500 mt-1">
                    {competitor.has_delivery ? "С доставкой" : "Без доставки"} • {competitor.seller_name || competitor.seller || ''}
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <div className="text-center">
                    <div className="flex items-center gap-1">
                      <span className="text-xl font-semibold">{Number(competitor.price).toLocaleString()} ₸</span>
                      {(competitor.price_change || competitor.priceChange || 0) > 0 ? (
                        <ArrowUp className="h-4 w-4 text-red-500" />
                      ) : (competitor.price_change || competitor.priceChange || 0) < 0 ? (
                        <ArrowDown className="h-4 w-4 text-green-500" />
                      ) : null}
                    </div>
                    {(competitor.price_change || competitor.priceChange || 0) !== 0 && (
                      <div className="text-xs text-gray-500">
                        {Math.abs(competitor.price_change || competitor.priceChange || 0).toLocaleString()} ₸
                      </div>
                    )}
                  </div>

                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Button size="sm" onClick={() => handleSetPrice(competitor.id)}>
                          Стать дешевле
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>Установить цену на 1₸ ниже</p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                </div>
              </div>
            </motion.div>
          ))
        ) : (
          <div className="text-center py-8 text-gray-500">
            Конкуренты не найдены
          </div>
        )}
      </div>
    </div>
  );
};

export default CompetitorsList;
