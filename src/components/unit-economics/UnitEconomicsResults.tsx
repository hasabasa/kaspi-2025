
import { Card, CardContent } from "@/components/ui/card";
import { motion } from "framer-motion";
import { TrendingUp, TrendingDown, AlertTriangle } from "lucide-react";

interface UnitEconomicsResultsProps {
  results: {
    costPrice: number;
    sellingPrice: number;
    commission: number;
    commissionPercent: number;
    deliveryCost: number;
    profit: number;
  };
}

const UnitEconomicsResults = ({ results }: UnitEconomicsResultsProps) => {
  const isProfitable = results.profit > 0;

  const profitMargin = ((results.profit / results.sellingPrice) * 100);
  const markupPercent = ((results.sellingPrice - results.costPrice) / results.costPrice * 100);
  const roi = ((results.profit / results.costPrice) * 100);

  return (
    <div className="space-y-6">
      {/* Простые метрики */}
      <div className="space-y-4">
        <div className="flex justify-between items-center p-3 border border-gray-200 dark:border-gray-700 rounded-lg">
          <span className="text-sm font-medium text-gray-900 dark:text-white">Себестоимость</span>
          <span className="font-medium text-gray-900 dark:text-white">{results.costPrice.toLocaleString()} ₸</span>
        </div>
        
        <div className="flex justify-between items-center p-3 border border-gray-200 dark:border-gray-700 rounded-lg">
          <span className="text-sm font-medium text-gray-900 dark:text-white">Цена продажи</span>
          <span className="font-medium text-gray-900 dark:text-white">{results.sellingPrice.toLocaleString()} ₸</span>
        </div>
        
        <div className="flex justify-between items-center p-3 border border-gray-200 dark:border-gray-700 rounded-lg">
          <span className="text-sm font-medium text-gray-900 dark:text-white">
            Комиссия Kaspi ({results.commissionPercent}%)
          </span>
          <span className="font-medium text-gray-900 dark:text-white">{results.commission.toLocaleString()} ₸</span>
        </div>
        
        <div className="flex justify-between items-center p-3 border border-gray-200 dark:border-gray-700 rounded-lg">
          <span className="text-sm font-medium text-gray-900 dark:text-white">Доставка</span>
          <span className="font-medium text-gray-900 dark:text-white">{results.deliveryCost.toLocaleString()} ₸</span>
        </div>
      </div>

      {/* Главный результат */}
      <div className={`p-6 rounded-lg border-2 ${
        isProfitable 
          ? "border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-900/10"
          : "border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/10"
      }`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {isProfitable ? (
              <TrendingUp className="h-6 w-6 text-green-600 dark:text-green-400" />
            ) : (
              <TrendingDown className="h-6 w-6 text-red-600 dark:text-red-400" />
            )}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Чистая прибыль</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Маржа: {profitMargin.toFixed(1)}%
              </p>
            </div>
          </div>
          <div className="text-right">
            <div className={`text-2xl font-bold ${
              isProfitable 
                ? "text-green-600 dark:text-green-400"
                : "text-red-600 dark:text-red-400"
            }`}>
              {results.profit.toLocaleString()} ₸
            </div>
          </div>
        </div>
      </div>

      {/* Дополнительные метрики */}
      <div className="grid grid-cols-2 gap-4">
        <div className="text-center p-3 border border-gray-200 dark:border-gray-700 rounded-lg">
          <div className="text-sm text-gray-600 dark:text-gray-400">Наценка</div>
          <div className="text-lg font-semibold text-gray-900 dark:text-white">{markupPercent.toFixed(1)}%</div>
        </div>
        <div className="text-center p-3 border border-gray-200 dark:border-gray-700 rounded-lg">
          <div className="text-sm text-gray-600 dark:text-gray-400">ROI</div>
          <div className="text-lg font-semibold text-gray-900 dark:text-white">{roi.toFixed(1)}%</div>
        </div>
      </div>

      {/* Простые рекомендации */}
      {!isProfitable && (
        <div className="p-4 bg-orange-50 dark:bg-orange-900/10 border border-orange-200 dark:border-orange-800 rounded-lg">
          <div className="flex items-start gap-3">
            <AlertTriangle className="h-5 w-5 text-orange-600 dark:text-orange-400 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-orange-800 dark:text-orange-200">
                Товар убыточен
              </p>
              <p className="text-sm text-orange-700 dark:text-orange-300 mt-1">
                Рекомендуется пересмотреть цену или найти поставщика с лучшими условиями
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UnitEconomicsResults;
