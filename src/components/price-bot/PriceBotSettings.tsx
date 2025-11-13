
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertCircle } from "lucide-react";
import { Product } from "@/types";
import { usePriceBotSettings } from "@/hooks/usePriceBotSettings";
import StrategySection from "./StrategySection";
import ProfitSection from "./ProfitSection";
import ActivationSection from "./ActivationSection";

interface PriceBotSettingsProps {
  product: Product;
  onSave: (settings: any) => void;
}

const PriceBotSettings = ({ product, onSave }: PriceBotSettingsProps) => {
  const {
    strategy,
    minProfit,
    isActive,
    isLoading,
    errors,
    handleSave,
    handleStrategyChange,
    handleMinProfitChange,
    handleActiveChange,
  } = usePriceBotSettings({ product, onSave });

  console.log('PriceBotSettings render - isActive:', isActive, 'productId:', product.id);

  return (
    <div className="space-y-4">
      {errors.length > 0 && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            {errors.map((error, index) => (
              <div key={index}>{error}</div>
            ))}
          </AlertDescription>
        </Alert>
      )}

      <StrategySection 
        strategy={strategy}
        onStrategyChange={handleStrategyChange}
      />

      <ProfitSection 
        minProfit={minProfit}
        onMinProfitChange={handleMinProfitChange}
      />

      <ActivationSection 
        isActive={isActive}
        onActiveChange={handleActiveChange}
      />

      <Button 
        onClick={handleSave} 
        className="w-full" 
        disabled={isLoading}
      >
        {isLoading ? 'Сохранение...' : 'Сохранить настройки'}
      </Button>
    </div>
  );
};

export default PriceBotSettings;
