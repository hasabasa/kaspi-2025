
import { useState, useEffect } from "react";
import { Product } from "@/types";
import { PricingStrategy, PriceBotSettings, PriceBotValidationResult } from "@/types/priceBotTypes";

interface UsePriceBotSettingsProps {
  product: Product;
  onSave: (settings: any) => void;
}

export const usePriceBotSettings = ({ product, onSave }: UsePriceBotSettingsProps) => {
  const [strategy, setStrategy] = useState<PricingStrategy>(PricingStrategy.BECOME_FIRST);
  const [minProfit, setMinProfit] = useState<number>(2000);
  const [isActive, setIsActive] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [errors, setErrors] = useState<string[]>([]);

  // Инициализация состояния при изменении продукта
  useEffect(() => {
    console.log('usePriceBotSettings: Initializing for product:', product.id);
    console.log('Product bot state:', product.botActive || product.bot_active);
    
    const botActiveState = product.botActive || product.bot_active || false;
    setIsActive(botActiveState);
    setMinProfit(product.minProfit || product.min_profit || 2000);
    setErrors([]);
  }, [product.id]);

  const validateSettings = (): PriceBotValidationResult => {
    const validationErrors: string[] = [];

    if (minProfit < 0) {
      validationErrors.push('Минимальная прибыль не может быть отрицательной');
    }

    if (minProfit > 100000) {
      validationErrors.push('Минимальная прибыль слишком большая');
    }

    return {
      isValid: validationErrors.length === 0,
      errors: validationErrors
    };
  };

  const handleSave = async () => {
    console.log('usePriceBotSettings: handleSave called');
    
    const validation = validateSettings();
    if (!validation.isValid) {
      setErrors(validation.errors);
      return;
    }

    setIsLoading(true);
    setErrors([]);

    try {
      await onSave({
        productId: product.id,
        strategy,
        minProfit,
        isActive,
      });
    } catch (error) {
      console.error('Error saving settings:', error);
      setErrors(['Ошибка при сохранении настроек']);
    } finally {
      setIsLoading(false);
    }
  };

  const handleStrategyChange = (newStrategy: PricingStrategy) => {
    setStrategy(newStrategy);
    setErrors([]);
  };

  const handleMinProfitChange = (value: number) => {
    setMinProfit(value);
    setErrors([]);
  };

  const handleActiveChange = (checked: boolean) => {
    console.log('usePriceBotSettings: Switch changed to:', checked);
    setIsActive(checked);
    setErrors([]);
  };

  return {
    // State
    strategy,
    minProfit,
    isActive,
    isLoading,
    errors,
    
    // Actions
    handleSave,
    handleStrategyChange,
    handleMinProfitChange,
    handleActiveChange,
    
    // Utils
    validateSettings
  };
};
