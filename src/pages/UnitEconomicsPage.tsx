
import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import UnitEconomicsForm from "@/components/unit-economics/UnitEconomicsForm";
import UnitEconomicsResults from "@/components/unit-economics/UnitEconomicsResults";
import { KaspiCommission, DeliveryRate } from "@/types";
import { calculateDeliveryCost, calculateCommission } from "@/lib/economicsUtils";
import { mockGoldCommissions, mockRedKreditCommissions, mockInstallmentCommissions } from "@/data/mockData";
// import { useStoreConnection } from "@/hooks/useStoreConnection";
// import ConnectStoreButton from "@/components/store/ConnectStoreButton";
// import LoadingScreen from "@/components/ui/loading-screen";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Calculator, FileText } from "lucide-react";
// Убираем мобильный хук для простоты
// import { useMobileOptimizedSimple as useMobileOptimized } from "@/hooks/useMobileOptimizedSimple";
import { cn } from "@/lib/utils";

const UnitEconomicsPage = () => {
  // Убираем зависимость от магазина для калькулятора
  // const { isConnected, loading: storeLoading } = useStoreConnection();
  // Убираем мобильный хук
  // const mobile = useMobileOptimized();
  
  const [unitData, setUnitData] = useState({
    costPrice: 10000,
    sellingPrice: 15000,
    category: "Электроника",
    weight: 1,
    deliveryScope: "По городу",
    paymentType: "Gold",
  });

  const [results, setResults] = useState({
    costPrice: 10000,
    sellingPrice: 15000,
    commission: 0,
    commissionPercent: 0,
    deliveryCost: 0,
    profit: 0,
  });

  useEffect(() => {
    const commissionPercent = calculateCommission(
      unitData.category,
      unitData.paymentType,
      mockGoldCommissions,
      mockRedKreditCommissions,
      mockInstallmentCommissions
    );

    const commissionAmount = (unitData.sellingPrice * commissionPercent) / 100;
    
    const deliveryCost = calculateDeliveryCost(
      unitData.sellingPrice,
      unitData.weight,
      unitData.deliveryScope
    );

    const profit = unitData.sellingPrice - unitData.costPrice - commissionAmount - deliveryCost;

    setResults({
      costPrice: unitData.costPrice,
      sellingPrice: unitData.sellingPrice,
      commission: commissionAmount,
      commissionPercent: commissionPercent,
      deliveryCost: deliveryCost,
      profit: profit,
    });
  }, [unitData]);

  // Убираем проверку загрузки магазинов - калькулятор работает независимо
  // if (storeLoading) {
  //   return <LoadingScreen text="Загрузка данных магазинов..." />;
  // }

  return (
    <div className="container mx-auto p-4 md:p-6 space-y-4 md:space-y-6">
      {/* Заголовок */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 text-center sm:text-left">
          <Calculator className="h-6 w-6 md:h-8 md:w-8 text-gray-600 dark:text-gray-400 mx-auto sm:mx-0" />
          <div>
            <h1 className="text-xl md:text-2xl font-bold text-gray-900 dark:text-white">
              Калькулятор прибыли
            </h1>
            <p className="text-sm md:text-base text-gray-600 dark:text-gray-400">
              Расчет прибыльности товаров с учетом комиссий Kaspi.kz
            </p>
          </div>
        </div>
      </div>

      {/* Адаптивные колонки */}
      <div className="grid gap-4 md:gap-6 grid-cols-1 lg:grid-cols-2">
        {/* Форма ввода */}
        <div>
          <Card>
            <CardHeader className="p-4 md:p-6">
              <CardTitle className="text-lg md:text-xl">
                Параметры товара
              </CardTitle>
              <CardDescription className="text-sm md:text-base">
                Введите данные для расчета
              </CardDescription>
            </CardHeader>
            <CardContent className="p-4 md:p-6 pt-0">
              <UnitEconomicsForm 
                data={unitData} 
                onChange={setUnitData} 
              />
            </CardContent>
          </Card>
        </div>

        {/* Результаты */}
        <div>
          <Card>
            <CardHeader className="p-4 md:p-6">
              <CardTitle className="flex items-center gap-2 text-lg md:text-xl">
                <FileText className="h-5 w-5 md:h-6 md:w-6" />
                Результаты расчета
              </CardTitle>
              <CardDescription className="text-sm md:text-base">
                Анализ прибыльности
              </CardDescription>
            </CardHeader>
            <CardContent className="p-4 md:p-6 pt-0">
              <UnitEconomicsResults results={results} />
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default UnitEconomicsPage;
