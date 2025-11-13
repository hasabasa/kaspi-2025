import React, { useState, useEffect } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Search, Filter, X, Power, PowerOff } from 'lucide-react';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';

export interface ProductFilters {
  search: string;
  botStatus: 'all' | 'enabled' | 'disabled';
  category: string;
  priceRange: {
    min: string;
    max: string;
  };
}

interface ProductFiltersProps {
  filters: ProductFilters;
  onFiltersChange: (filters: ProductFilters) => void;
  categories: string[];
  resultCount?: number;
}

const ProductFiltersComponent: React.FC<ProductFiltersProps> = ({
  filters,
  onFiltersChange,
  categories,
  resultCount
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [localFilters, setLocalFilters] = useState(filters);

  useEffect(() => {
    setLocalFilters(filters);
  }, [filters]);

  const handleSearchChange = (value: string) => {
    const newFilters = { ...localFilters, search: value };
    setLocalFilters(newFilters);
    onFiltersChange(newFilters);
  };

  const handleFilterChange = (key: keyof ProductFilters, value: any) => {
    const newFilters = { ...localFilters, [key]: value };
    setLocalFilters(newFilters);
    onFiltersChange(newFilters);
  };

  const handlePriceRangeChange = (type: 'min' | 'max', value: string) => {
    const newFilters = {
      ...localFilters,
      priceRange: {
        ...localFilters.priceRange,
        [type]: value
      }
    };
    setLocalFilters(newFilters);
    onFiltersChange(newFilters);
  };

  const clearAllFilters = () => {
    const clearedFilters: ProductFilters = {
      search: '',
      botStatus: 'all',
      category: '',
      priceRange: { min: '', max: '' }
    };
    setLocalFilters(clearedFilters);
    onFiltersChange(clearedFilters);
  };

  const hasActiveFilters = localFilters.search || 
                          localFilters.botStatus !== 'all' || 
                          localFilters.category || 
                          localFilters.priceRange.min || 
                          localFilters.priceRange.max;

  const getActiveFiltersCount = () => {
    let count = 0;
    if (localFilters.search) count++;
    if (localFilters.botStatus !== 'all') count++;
    if (localFilters.category) count++;
    if (localFilters.priceRange.min || localFilters.priceRange.max) count++;
    return count;
  };

  return (
    <Card className="mb-6">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Search className="h-5 w-5 text-primary" />
            <CardTitle>Поиск и фильтры</CardTitle>
            {hasActiveFilters && (
              <Badge variant="secondary">
                {getActiveFiltersCount()} активных
              </Badge>
            )}
          </div>
          <div className="flex items-center gap-2">
            {resultCount !== undefined && (
              <div className="text-sm text-muted-foreground">
                Найдено: {resultCount}
              </div>
            )}
            {hasActiveFilters && (
              <Button
                variant="ghost"
                size="sm"
                onClick={clearAllFilters}
                className="text-muted-foreground hover:text-foreground"
              >
                <X className="h-4 w-4 mr-1" />
                Сбросить
              </Button>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Поиск по SKU/названию */}
        <div className="space-y-2">
          <Label htmlFor="search">Поиск по SKU или названию товара</Label>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
            <Input
              id="search"
              placeholder="Введите SKU или название..."
              value={localFilters.search}
              onChange={(e) => handleSearchChange(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>

        {/* Расширенные фильтры */}
        <Collapsible open={isOpen} onOpenChange={setIsOpen}>
          <CollapsibleTrigger asChild>
            <Button variant="outline" className="w-full justify-between">
              <div className="flex items-center gap-2">
                <Filter className="h-4 w-4" />
                Дополнительные фильтры
              </div>
              <span className="text-muted-foreground">
                {isOpen ? '−' : '+'}
              </span>
            </Button>
          </CollapsibleTrigger>
          
          <CollapsibleContent className="space-y-4 mt-4">
            {/* Статус бота */}
            <div className="space-y-2">
              <Label>Статус прайс-бота</Label>
              <Select
                value={localFilters.botStatus}
                onValueChange={(value: 'all' | 'enabled' | 'disabled') => 
                  handleFilterChange('botStatus', value)
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">
                    <div className="flex items-center gap-2">
                      <Filter className="h-4 w-4" />
                      Все товары
                    </div>
                  </SelectItem>
                  <SelectItem value="enabled">
                    <div className="flex items-center gap-2">
                      <Power className="h-4 w-4 text-green-500" />
                      Бот активен
                    </div>
                  </SelectItem>
                  <SelectItem value="disabled">
                    <div className="flex items-center gap-2">
                      <PowerOff className="h-4 w-4 text-red-500" />
                      Бот неактивен
                    </div>
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Категория */}
            <div className="space-y-2">
              <Label>Категория товара</Label>
              <Select
                value={localFilters.category}
                onValueChange={(value) => handleFilterChange('category', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Выберите категорию" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Все категории</SelectItem>
                  {categories.map((category) => (
                    <SelectItem key={category} value={category}>
                      {category}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Диапазон цен */}
            <div className="space-y-2">
              <Label>Диапазон цен (₸)</Label>
              <div className="flex items-center gap-2">
                <Input
                  type="number"
                  placeholder="От"
                  value={localFilters.priceRange.min}
                  onChange={(e) => handlePriceRangeChange('min', e.target.value)}
                  min="0"
                />
                <span className="text-muted-foreground">—</span>
                <Input
                  type="number"
                  placeholder="До"
                  value={localFilters.priceRange.max}
                  onChange={(e) => handlePriceRangeChange('max', e.target.value)}
                  min="0"
                />
              </div>
            </div>
          </CollapsibleContent>
        </Collapsible>

        {/* Активные фильтры */}
        {hasActiveFilters && (
          <div className="flex flex-wrap gap-2 pt-2 border-t">
            {localFilters.search && (
              <Badge variant="secondary" className="flex items-center gap-1">
                <Search className="h-3 w-3" />
                Поиск: "{localFilters.search}"
                <button
                  onClick={() => handleSearchChange('')}
                  className="ml-1 hover:bg-background rounded-full"
                >
                  <X className="h-3 w-3" />
                </button>
              </Badge>
            )}
            
            {localFilters.botStatus !== 'all' && (
              <Badge variant="secondary" className="flex items-center gap-1">
                {localFilters.botStatus === 'enabled' ? (
                  <Power className="h-3 w-3 text-green-500" />
                ) : (
                  <PowerOff className="h-3 w-3 text-red-500" />
                )}
                {localFilters.botStatus === 'enabled' ? 'Бот активен' : 'Бот неактивен'}
                <button
                  onClick={() => handleFilterChange('botStatus', 'all')}
                  className="ml-1 hover:bg-background rounded-full"
                >
                  <X className="h-3 w-3" />
                </button>
              </Badge>
            )}
            
            {localFilters.category && (
              <Badge variant="secondary" className="flex items-center gap-1">
                {localFilters.category}
                <button
                  onClick={() => handleFilterChange('category', '')}
                  className="ml-1 hover:bg-background rounded-full"
                >
                  <X className="h-3 w-3" />
                </button>
              </Badge>
            )}
            
            {(localFilters.priceRange.min || localFilters.priceRange.max) && (
              <Badge variant="secondary" className="flex items-center gap-1">
                Цена: {localFilters.priceRange.min || '0'} — {localFilters.priceRange.max || '∞'} ₸
                <button
                  onClick={() => handlePriceRangeChange('min', '') && handlePriceRangeChange('max', '')}
                  className="ml-1 hover:bg-background rounded-full"
                >
                  <X className="h-3 w-3" />
                </button>
              </Badge>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default ProductFiltersComponent;
