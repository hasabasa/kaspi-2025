
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { PricingStrategy } from "@/types/priceBotTypes";

interface StrategySectionProps {
  strategy: PricingStrategy;
  onStrategyChange: (strategy: PricingStrategy) => void;
}

const StrategySection = ({ strategy, onStrategyChange }: StrategySectionProps) => {
  return (
    <div>
      <h3 className="text-lg font-medium mb-3">Стратегия бота</h3>
      <RadioGroup value={strategy} onValueChange={onStrategyChange} className="space-y-2">
        <div className="flex items-center space-x-2">
          <RadioGroupItem value={PricingStrategy.BECOME_FIRST} id="become-first" />
          <Label htmlFor="become-first" className="font-normal">🥇 Стань первым (на 1 тг дешевле)</Label>
        </div>
        <div className="flex items-center space-x-2">
          <RadioGroupItem value={PricingStrategy.EQUAL_PRICE} id="equal-price" />
          <Label htmlFor="equal-price" className="font-normal">⚖️ Равная цена с конкурентом</Label>
        </div>
      </RadioGroup>
    </div>
  );
};

export default StrategySection;
