
import { supabase } from "@/integrations/supabase/client";
import { SaveSettingsRequest, PriceBotValidationResult } from "@/types/priceBotTypes";

export class PriceBotService {
  static validateBusinessRules(settings: SaveSettingsRequest): PriceBotValidationResult {
    const errors: string[] = [];

    // Бизнес-правила валидации
    if (settings.minProfit < 0) {
      errors.push('Минимальная прибыль не может быть отрицательной');
    }

    if (settings.minProfit > 1000000) {
      errors.push('Минимальная прибыль не может превышать 1,000,000 ₸');
    }

    if (settings.maxProfit && settings.maxProfit < settings.minProfit) {
      errors.push('Максимальная прибыль не может быть меньше минимальной');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  static async saveSettings(settings: SaveSettingsRequest, isDemo: boolean = false): Promise<void> {
    console.log('PriceBotService: Saving settings:', settings);

    // Валидация бизнес-правил
    const validation = this.validateBusinessRules(settings);
    if (!validation.isValid) {
      throw new Error(validation.errors.join(', '));
    }

    // В демо-режиме просто логируем
    if (isDemo) {
      console.log('PriceBotService: Demo mode - settings would be saved:', settings);
      return;
    }

    // Сохранение в базу данных
    const { error } = await supabase
      .from('products')
      .update({
        bot_active: settings.isActive,
        min_profit: settings.minProfit,
        max_profit: settings.maxProfit,
        updated_at: new Date().toISOString()
      })
      .eq('id', settings.productId);

    if (error) {
      console.error('PriceBotService: Database error:', error);
      throw error;
    }

    console.log('PriceBotService: Settings saved successfully');
  }

  static async toggleBotStatus(productIds: string[], isActive: boolean, isDemo: boolean = false): Promise<void> {
    console.log('PriceBotService: Toggling bot status:', { productIds, isActive });

    if (isDemo) {
      console.log('PriceBotService: Demo mode - bot status would be toggled');
      return;
    }

    const { error } = await supabase
      .from('products')
      .update({
        bot_active: isActive,
        updated_at: new Date().toISOString()
      })
      .in('id', productIds);

    if (error) {
      console.error('PriceBotService: Error toggling bot status:', error);
      throw error;
    }

    console.log('PriceBotService: Bot status toggled successfully');
  }
}
