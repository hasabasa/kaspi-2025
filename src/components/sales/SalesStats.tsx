
import { Card, CardContent } from "@/components/ui/card";
import { SalesData } from "@/types";
import { filterDataByDateRange, calculateTotalSales, calculateAverageOrderValue, calculateTotalOrders } from "@/lib/salesUtils";
import { useIsMobile } from "@/hooks/use-mobile";
import { TrendingUp, ShoppingCart, DollarSign } from "lucide-react";

interface SalesStatsProps {
  salesData: SalesData[];
  dateRange: {
    from?: Date;
    to?: Date;
  };
}

const SalesStats = ({ salesData, dateRange }: SalesStatsProps) => {
  const isMobile = useIsMobile();
  const filteredData = filterDataByDateRange(salesData, dateRange);
  
  const totalSales = calculateTotalSales(filteredData);
  const averageOrderValue = calculateAverageOrderValue(filteredData);
  const totalOrders = calculateTotalOrders(filteredData);

  const stats = [
    {
      title: isMobile ? "Продажи" : "Всего продаж",
      value: `${totalSales.toLocaleString()} ₸`,
      description: isMobile ? "Общая сумма" : "Общая сумма заказов",
      trend: filteredData.length > 1 ? filteredData[filteredData.length - 1].amount > filteredData[filteredData.length - 2].amount : undefined,
      icon: DollarSign,
      gradient: "from-emerald-500 to-teal-600",
      bgGradient: "from-emerald-50 to-teal-50"
    },
    {
      title: isMobile ? "Ср. чек" : "Средний чек",
      value: `${averageOrderValue.toLocaleString()} ₸`,
      description: isMobile ? "За заказ" : "Средняя сумма заказа",
      icon: TrendingUp,
      gradient: "from-blue-500 to-indigo-600",
      bgGradient: "from-blue-50 to-indigo-50"
    },
    {
      title: isMobile ? "Заказы" : "Кол-во заказов",
      value: totalOrders,
      description: isMobile ? "Всего" : "Общее количество заказов",
      icon: ShoppingCart,
      gradient: "from-purple-500 to-pink-600",
      bgGradient: "from-purple-50 to-pink-50"
    }
  ];

  return (
    <>
      {stats.map((stat, index) => {
        const IconComponent = stat.icon;
        return (
          <Card 
            key={index} 
            className={`relative overflow-hidden bg-gradient-to-br ${stat.bgGradient} border-0 shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105`}
          >
            <div className={`absolute top-0 right-0 w-20 h-20 bg-gradient-to-br ${stat.gradient} opacity-10 rounded-full transform translate-x-6 -translate-y-6`} />
            <CardContent className={`${isMobile ? 'pt-4 p-4' : 'pt-6'} relative z-10`}>
              <div className="flex items-start justify-between">
                <div className="flex flex-col space-y-1.5 md:space-y-2">
                  <p className={`${isMobile ? 'text-xs' : 'text-sm'} text-muted-foreground font-medium`}>
                    {stat.title}
                  </p>
                  <div className={`${isMobile ? 'text-lg' : 'text-2xl'} font-bold bg-gradient-to-r ${stat.gradient} bg-clip-text text-transparent`}>
                    {stat.value}
                  </div>
                  <p className={`${isMobile ? 'text-xs' : 'text-xs'} text-muted-foreground`}>
                    {stat.description}
                  </p>
                </div>
                <div className={`p-2 rounded-xl bg-gradient-to-br ${stat.gradient} shadow-lg`}>
                  <IconComponent className={`${isMobile ? 'h-4 w-4' : 'h-5 w-5'} text-white`} />
                </div>
              </div>
            </CardContent>
          </Card>
        );
      })}
    </>
  );
};

export default SalesStats;
