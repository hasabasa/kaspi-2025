import React, { useState } from 'react';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Checkbox } from '@/components/ui/checkbox';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Switch } from '@/components/ui/switch';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { 
  Power, 
  PowerOff, 
  Edit3, 
  Save, 
  X, 
  TrendingUp, 
  TrendingDown,
  Minus,
  DollarSign,
  Package
} from 'lucide-react';
import { toast } from 'sonner';
import { Product } from '@/services/kaspiStoreService';

interface ProductTableProps {
  products: Product[];
  selectedProducts: string[];
  onSelectionChange: (selectedIds: string[]) => void;
  onProductUpdate?: (productId: string, updates: Partial<Product>) => void;
  isLoading?: boolean;
}

interface EditingProduct {
  id: string;
  minPrice: string;
  maxPrice: string;
  priceStep: string;
}

const ProductTable: React.FC<ProductTableProps> = ({
  products,
  selectedProducts,
  onSelectionChange,
  onProductUpdate,
  isLoading = false
}) => {
  const [editingProduct, setEditingProduct] = useState<EditingProduct | null>(null);

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      onSelectionChange(products.map(p => p.id));
    } else {
      onSelectionChange([]);
    }
  };

  const handleSelectProduct = (productId: string, checked: boolean) => {
    if (checked) {
      onSelectionChange([...selectedProducts, productId]);
    } else {
      onSelectionChange(selectedProducts.filter(id => id !== productId));
    }
  };

  const handleBotToggle = (product: Product, enabled: boolean) => {
    if (onProductUpdate) {
      onProductUpdate(product.id, { bot_enabled: enabled });
      toast.success(
        enabled 
          ? `Прайс-бот включен для "${product.name}"` 
          : `Прайс-бот выключен для "${product.name}"`
      );
    }
  };

  const startEditing = (product: Product) => {
    setEditingProduct({
      id: product.id,
      minPrice: product.min_price?.toString() || '',
      maxPrice: product.max_price?.toString() || '',
      priceStep: product.price_step?.toString() || ''
    });
  };

  const cancelEditing = () => {
    setEditingProduct(null);
  };

  const saveEditing = () => {
    if (!editingProduct || !onProductUpdate) return;

    const updates: Partial<Product> = {};
    
    if (editingProduct.minPrice) {
      const minPrice = parseFloat(editingProduct.minPrice);
      if (!isNaN(minPrice) && minPrice > 0) {
        updates.min_price = minPrice;
      }
    }
    
    if (editingProduct.maxPrice) {
      const maxPrice = parseFloat(editingProduct.maxPrice);
      if (!isNaN(maxPrice) && maxPrice > 0) {
        updates.max_price = maxPrice;
      }
    }
    
    if (editingProduct.priceStep) {
      const priceStep = parseFloat(editingProduct.priceStep);
      if (!isNaN(priceStep) && priceStep > 0) {
        updates.price_step = priceStep;
      }
    }

    // Проверяем соотношение цен
    if (updates.min_price && updates.max_price && updates.min_price >= updates.max_price) {
      toast.error('Минимальная цена должна быть меньше максимальной');
      return;
    }

    onProductUpdate(editingProduct.id, updates);
    setEditingProduct(null);
    toast.success('Настройки товара обновлены');
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('ru-KZ').format(price) + ' ₸';
  };

  const getPositionIcon = (current?: number, target?: number) => {
    if (!current || !target) return <Minus className="h-4 w-4 text-muted-foreground" />;
    
    if (current < target) {
      return <TrendingDown className="h-4 w-4 text-red-500" />;
    } else if (current > target) {
      return <TrendingUp className="h-4 w-4 text-green-500" />;
    } else {
      return <Minus className="h-4 w-4 text-blue-500" />;
    }
  };

  const isAllSelected = products.length > 0 && selectedProducts.length === products.length;
  const isPartiallySelected = selectedProducts.length > 0 && selectedProducts.length < products.length;

  if (products.length === 0) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-12">
          <Package className="h-12 w-12 text-muted-foreground mb-4" />
          <p className="text-lg font-medium">Товары не найдены</p>
          <p className="text-muted-foreground">Попробуйте изменить фильтры поиска</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Package className="h-5 w-5" />
            Товары ({products.length})
          </CardTitle>
          <div className="text-sm text-muted-foreground">
            Выбрано: {selectedProducts.length} из {products.length}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="rounded-md border overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-12">
                  <Checkbox 
                    checked={isAllSelected}
                    ref={(ref) => {
                      if (ref) ref.indeterminate = isPartiallySelected && !isAllSelected;
                    }}
                    onCheckedChange={handleSelectAll}
                  />
                </TableHead>
                <TableHead>SKU</TableHead>
                <TableHead>Название</TableHead>
                <TableHead>Бренд</TableHead>
                <TableHead>Цена</TableHead>
                <TableHead>Остаток</TableHead>
                <TableHead>Прайс-бот</TableHead>
                <TableHead>Мин/Макс цена</TableHead>
                <TableHead>Шаг</TableHead>
                <TableHead>Позиция</TableHead>
                <TableHead className="w-24">Действия</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {products.map((product) => {
                const isEditing = editingProduct?.id === product.id;
                const isSelected = selectedProducts.includes(product.id);
                
                return (
                  <TableRow 
                    key={product.id}
                    className={isSelected ? 'bg-muted/50' : undefined}
                  >
                    <TableCell>
                      <Checkbox 
                        checked={isSelected}
                        onCheckedChange={(checked) => handleSelectProduct(product.id, !!checked)}
                      />
                    </TableCell>
                    
                    <TableCell className="font-mono text-sm">
                      {product.article}
                    </TableCell>
                    
                    <TableCell className="max-w-xs">
                      <div className="truncate" title={product.name}>
                        {product.name}
                      </div>
                    </TableCell>
                    
                    <TableCell>
                      <Badge variant="outline">{product.brand}</Badge>
                    </TableCell>
                    
                    <TableCell className="font-medium">
                      {formatPrice(product.price)}
                    </TableCell>
                    
                    <TableCell>
                      <Badge variant={product.stock > 0 ? 'default' : 'destructive'}>
                        {product.stock} шт
                      </Badge>
                    </TableCell>
                    
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Switch
                          checked={product.bot_enabled}
                          onCheckedChange={(checked) => handleBotToggle(product, checked)}
                          disabled={isLoading}
                        />
                        {product.bot_enabled ? (
                          <Power className="h-4 w-4 text-green-500" />
                        ) : (
                          <PowerOff className="h-4 w-4 text-red-500" />
                        )}
                      </div>
                    </TableCell>
                    
                    <TableCell>
                      {isEditing ? (
                        <div className="space-y-1">
                          <Input
                            type="number"
                            placeholder="Мин"
                            value={editingProduct.minPrice}
                            onChange={(e) => setEditingProduct(prev => 
                              prev ? { ...prev, minPrice: e.target.value } : null
                            )}
                            className="h-8 text-xs"
                          />
                          <Input
                            type="number"
                            placeholder="Макс"
                            value={editingProduct.maxPrice}
                            onChange={(e) => setEditingProduct(prev => 
                              prev ? { ...prev, maxPrice: e.target.value } : null
                            )}
                            className="h-8 text-xs"
                          />
                        </div>
                      ) : (
                        <div className="text-sm">
                          <div className="text-green-600">
                            {product.min_price ? formatPrice(product.min_price) : '—'}
                          </div>
                          <div className="text-red-600">
                            {product.max_price ? formatPrice(product.max_price) : '—'}
                          </div>
                        </div>
                      )}
                    </TableCell>
                    
                    <TableCell>
                      {isEditing ? (
                        <Input
                          type="number"
                          placeholder="Шаг"
                          value={editingProduct.priceStep}
                          onChange={(e) => setEditingProduct(prev => 
                            prev ? { ...prev, priceStep: e.target.value } : null
                          )}
                          className="h-8 text-xs w-20"
                        />
                      ) : (
                        <div className="text-sm">
                          {product.price_step ? formatPrice(product.price_step) : '—'}
                        </div>
                      )}
                    </TableCell>
                    
                    <TableCell>
                      <div className="flex items-center gap-2">
                        {getPositionIcon(product.current_position, product.target_position)}
                        <div className="text-sm">
                          <div>{product.current_position || '—'}</div>
                          {product.target_position && (
                            <div className="text-muted-foreground">
                              ↗ {product.target_position}
                            </div>
                          )}
                        </div>
                      </div>
                    </TableCell>
                    
                    <TableCell>
                      {isEditing ? (
                        <div className="flex items-center gap-1">
                          <Button 
                            size="sm" 
                            variant="default"
                            onClick={saveEditing}
                            className="h-8 w-8 p-0"
                          >
                            <Save className="h-3 w-3" />
                          </Button>
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={cancelEditing}
                            className="h-8 w-8 p-0"
                          >
                            <X className="h-3 w-3" />
                          </Button>
                        </div>
                      ) : (
                        <Button 
                          size="sm" 
                          variant="ghost"
                          onClick={() => startEditing(product)}
                          className="h-8 w-8 p-0"
                          disabled={isLoading}
                        >
                          <Edit3 className="h-3 w-3" />
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
};

export default ProductTable;
