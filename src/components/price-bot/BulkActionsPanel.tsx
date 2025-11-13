import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import { AlertCircle, Settings, Power, DollarSign, TrendingUp, CheckCircle2 } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { toast } from 'sonner';
import kaspiStoreService from '@/services/kaspiStoreService';

interface BulkActionsPanelProps {
  selectedProducts: string[];
  storeId: string;
  onUpdate?: () => void;
  totalProducts: number;
}

const BulkActionsPanel: React.FC<BulkActionsPanelProps> = ({
  selectedProducts,
  storeId,
  onUpdate,
  totalProducts
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [bulkSettings, setBulkSettings] = useState({
    botEnabled: false,
    setBotEnabled: false,
    minPrice: '',
    setMinPrice: false,
    maxPrice: '',
    setMaxPrice: false,
    priceStep: '',
    setPriceStep: false,
  });

  const handleBulkUpdate = async () => {
    if (selectedProducts.length === 0) {
      toast.error('Выберите товары для обновления');
      return;
    }

    // Проверяем, что хотя бы одна настройка выбрана
    const hasAnySettings = bulkSettings.setBotEnabled || 
                          bulkSettings.setMinPrice || 
                          bulkSettings.setMaxPrice || 
                          bulkSettings.setPriceStep;

    if (!hasAnySettings) {
      toast.error('Выберите хотя бы одну настройку для обновления');
      return;
    }

    setIsLoading(true);

    try {
      const settings: any = {};
      
      if (bulkSettings.setBotEnabled) {
        settings.bot_enabled = bulkSettings.botEnabled;
      }
      
      if (bulkSettings.setMinPrice && bulkSettings.minPrice) {
        const minPrice = parseFloat(bulkSettings.minPrice);
        if (isNaN(minPrice) || minPrice < 0) {
          throw new Error('Минимальная цена должна быть положительным числом');
        }
        settings.min_price = minPrice;
      }
      
      if (bulkSettings.setMaxPrice && bulkSettings.maxPrice) {
        const maxPrice = parseFloat(bulkSettings.maxPrice);
        if (isNaN(maxPrice) || maxPrice < 0) {
          throw new Error('Максимальная цена должна быть положительным числом');
        }
        settings.max_price = maxPrice;
      }
      
      if (bulkSettings.setPriceStep && bulkSettings.priceStep) {
        const priceStep = parseFloat(bulkSettings.priceStep);
        if (isNaN(priceStep) || priceStep <= 0) {
          throw new Error('Шаг изменения цены должен быть положительным числом');
        }
        settings.price_step = priceStep;
      }

      // Проверяем соотношение цен
      if (settings.min_price && settings.max_price && settings.min_price >= settings.max_price) {
        throw new Error('Минимальная цена должна быть меньше максимальной');
      }

      const result = await kaspiStoreService.bulkUpdateBotSettings({
        store_id: storeId,
        product_ids: selectedProducts,
        settings
      });

      toast.success(`Успешно обновлено ${result.updated_count} товаров`);
      
      // Сброс настроек
      setBulkSettings({
        botEnabled: false,
        setBotEnabled: false,
        minPrice: '',
        setMinPrice: false,
        maxPrice: '',
        setMaxPrice: false,
        priceStep: '',
        setPriceStep: false,
      });

      if (onUpdate) {
        onUpdate();
      }

    } catch (error: any) {
      console.error('Error updating products:', error);
      toast.error(error.message || 'Ошибка при обновлении товаров');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectAllProducts = () => {
    if (selectedProducts.length === totalProducts) {
      // Если все выбраны, сбрасываем
      if (onUpdate) onUpdate();
    } else {
      // Иначе выбираем все
      if (onUpdate) onUpdate();
    }
  };

  return (
    <Card className="mb-6">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Settings className="h-5 w-5 text-primary" />
            <CardTitle>Массовые настройки</CardTitle>
          </div>
          <Badge variant="secondary">
            {selectedProducts.length} из {totalProducts} выбрано
          </Badge>
        </div>
        <CardDescription>
          Настройте параметры прайс-бота для выбранных товаров
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {selectedProducts.length === 0 && (
          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              Выберите товары из списка ниже, чтобы применить массовые настройки
            </AlertDescription>
          </Alert>
        )}

        <div className="flex items-center gap-4">
          <Button
            variant="outline"
            size="sm"
            onClick={handleSelectAllProducts}
          >
            {selectedProducts.length === totalProducts ? 'Снять все' : 'Выбрать все'}
          </Button>
          
          {selectedProducts.length > 0 && (
            <div className="text-sm text-muted-foreground">
              Выбрано товаров: {selectedProducts.length}
            </div>
          )}
        </div>

        <Separator />

        {/* Включение/выключение бота */}
        <div className="space-y-3">
          <div className="flex items-center space-x-2">
            <Checkbox 
              id="set-bot-enabled"
              checked={bulkSettings.setBotEnabled}
              onCheckedChange={(checked) => 
                setBulkSettings(prev => ({ ...prev, setBotEnabled: !!checked }))
              }
            />
            <Label htmlFor="set-bot-enabled" className="flex items-center gap-2">
              <Power className="h-4 w-4" />
              Управление ботом
            </Label>
          </div>
          
          {bulkSettings.setBotEnabled && (
            <div className="ml-6 flex items-center gap-4">
              <Label className="flex items-center space-x-2">
                <Checkbox 
                  checked={bulkSettings.botEnabled}
                  onCheckedChange={(checked) => 
                    setBulkSettings(prev => ({ ...prev, botEnabled: !!checked }))
                  }
                />
                <span>{bulkSettings.botEnabled ? 'Включить бот' : 'Выключить бот'}</span>
              </Label>
            </div>
          )}
        </div>

        <Separator />

        {/* Минимальная цена */}
        <div className="space-y-3">
          <div className="flex items-center space-x-2">
            <Checkbox 
              id="set-min-price"
              checked={bulkSettings.setMinPrice}
              onCheckedChange={(checked) => 
                setBulkSettings(prev => ({ ...prev, setMinPrice: !!checked }))
              }
            />
            <Label htmlFor="set-min-price" className="flex items-center gap-2">
              <DollarSign className="h-4 w-4" />
              Минимальная цена (₸)
            </Label>
          </div>
          
          {bulkSettings.setMinPrice && (
            <div className="ml-6">
              <Input
                type="number"
                placeholder="Введите минимальную цену"
                value={bulkSettings.minPrice}
                onChange={(e) => setBulkSettings(prev => ({ ...prev, minPrice: e.target.value }))}
                min="0"
                step="1"
              />
            </div>
          )}
        </div>

        <Separator />

        {/* Максимальная цена */}
        <div className="space-y-3">
          <div className="flex items-center space-x-2">
            <Checkbox 
              id="set-max-price"
              checked={bulkSettings.setMaxPrice}
              onCheckedChange={(checked) => 
                setBulkSettings(prev => ({ ...prev, setMaxPrice: !!checked }))
              }
            />
            <Label htmlFor="set-max-price" className="flex items-center gap-2">
              <DollarSign className="h-4 w-4" />
              Максимальная цена (₸)
            </Label>
          </div>
          
          {bulkSettings.setMaxPrice && (
            <div className="ml-6">
              <Input
                type="number"
                placeholder="Введите максимальную цену"
                value={bulkSettings.maxPrice}
                onChange={(e) => setBulkSettings(prev => ({ ...prev, maxPrice: e.target.value }))}
                min="0"
                step="1"
              />
            </div>
          )}
        </div>

        <Separator />

        {/* Шаг изменения цены */}
        <div className="space-y-3">
          <div className="flex items-center space-x-2">
            <Checkbox 
              id="set-price-step"
              checked={bulkSettings.setPriceStep}
              onCheckedChange={(checked) => 
                setBulkSettings(prev => ({ ...prev, setPriceStep: !!checked }))
              }
            />
            <Label htmlFor="set-price-step" className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              Шаг изменения цены (₸)
            </Label>
          </div>
          
          {bulkSettings.setPriceStep && (
            <div className="ml-6">
              <Input
                type="number"
                placeholder="Введите шаг изменения цены"
                value={bulkSettings.priceStep}
                onChange={(e) => setBulkSettings(prev => ({ ...prev, priceStep: e.target.value }))}
                min="1"
                step="1"
              />
              <div className="text-xs text-muted-foreground mt-1">
                На сколько тенге бот будет изменять цену за раз
              </div>
            </div>
          )}
        </div>

        <Separator />

        <div className="flex items-center gap-3">
          <Button 
            onClick={handleBulkUpdate} 
            disabled={isLoading || selectedProducts.length === 0}
            className="flex items-center gap-2"
          >
            {isLoading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                Обновление...
              </>
            ) : (
              <>
                <CheckCircle2 className="h-4 w-4" />
                Применить настройки
              </>
            )}
          </Button>

          {selectedProducts.length > 0 && (
            <div className="text-sm text-muted-foreground">
              к {selectedProducts.length} товарам
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default BulkActionsPanel;
