
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";

interface ActivationSectionProps {
  isActive: boolean;
  onActiveChange: (checked: boolean) => void;
}

const ActivationSection = ({ isActive, onActiveChange }: ActivationSectionProps) => {
  return (
    <div className="space-y-3">
      <h3 className="text-lg font-medium">Активация бота</h3>
      
      <div className="flex items-center space-x-2">
        <Switch 
          id="bot-active" 
          checked={isActive} 
          onCheckedChange={onActiveChange}
        />
        <Label htmlFor="bot-active">
          {isActive ? 'Бот активен' : 'Бот выключен'}
        </Label>
      </div>
    </div>
  );
};

export default ActivationSection;
