
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";

interface ProfitSectionProps {
  minProfit: number;
  onMinProfitChange: (value: number) => void;
}

const ProfitSection = ({ minProfit, onMinProfitChange }: ProfitSectionProps) => {
  return (
    <div className="space-y-3">
      <h3 className="text-lg font-medium">Настройки прибыли</h3>
      
      <div className="space-y-2">
        <Label htmlFor="min-profit">Минимальная прибыль (₸)</Label>
        <Input 
          id="min-profit" 
          type="number" 
          value={minProfit} 
          onChange={(e) => onMinProfitChange(parseInt(e.target.value) || 0)} 
        />
        <p className="text-sm text-gray-500">Бот не опустит цену ниже этого значения прибыли</p>
      </div>
    </div>
  );
};

export default ProfitSection;
