
export enum PricingStrategy {
  BECOME_FIRST = 'become-first',
  EQUAL_PRICE = 'equal-price'
}

export interface PriceBotSettings {
  productId: string;
  strategy: PricingStrategy;
  minProfit: number;
  maxProfit?: number;
  isActive: boolean;
}

export interface PriceBotValidationResult {
  isValid: boolean;
  errors: string[];
}

export interface SaveSettingsRequest {
  productId: string;
  strategy: PricingStrategy;
  minProfit: number;
  maxProfit?: number;
  isActive: boolean;
}
