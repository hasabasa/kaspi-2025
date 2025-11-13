
import { motion } from "framer-motion";
import { Badge } from "@/components/ui/badge";
import { Product } from "@/types";
import { useState } from "react";
import PopoverSettings from "./PopoverSettings";

interface ProductListProps {
  products: Product[];
  activeProductId: string | null;
  onProductSelect: (productId: string) => void;
  onSettingsSave?: (settings: any) => void;
}

const ProductList = ({ products, activeProductId, onProductSelect, onSettingsSave }: ProductListProps) => {
  const [popoverProduct, setPopoverProduct] = useState<Product | null>(null);
  const [triggerElement, setTriggerElement] = useState<HTMLElement | null>(null);

  if (products.length === 0) {
    return <div className="text-center py-6 text-gray-500">Товары не найдены</div>;
  }

  const handleProductClick = (product: Product, event: React.MouseEvent<HTMLDivElement>) => {
    const target = event.currentTarget;
    setTriggerElement(target);
    setPopoverProduct(product);
    onProductSelect(product.id);
  };

  const handlePopoverClose = () => {
    setPopoverProduct(null);
    setTriggerElement(null);
  };

  const handleSettingsSave = (settings: any) => {
    if (onSettingsSave) {
      onSettingsSave(settings);
    }
    // Не закрываем popover автоматически, пользователь может сам закрыть
  };

  return (
    <>
      <div className="space-y-3 max-h-[600px] overflow-y-auto pr-2">
        {products.map((product) => (
          <motion.div
            key={product.id}
            whileHover={{ scale: 1.01 }}
            whileTap={{ scale: 0.99 }}
            onClick={(event) => handleProductClick(product, event)}
            className={`p-3 rounded-xl cursor-pointer transition-all ${
              activeProductId === product.id
                ? 'bg-primary text-primary-foreground'
                : 'bg-card hover:bg-gray-100'
            }`}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-center">
                <div className="h-10 w-10 rounded-lg bg-gray-200 mr-3 overflow-hidden">
                  {(product.image || product.image_url) && (
                    <img 
                      src={product.image || product.image_url} 
                      alt={product.name} 
                      className="h-full w-full object-cover"
                    />
                  )}
                </div>
                <div>
                  <div className="font-medium line-clamp-2">{product.name}</div>
                  <div className="text-sm mt-1 flex items-center">
                    <span className={activeProductId === product.id ? 'text-primary-foreground' : 'text-gray-500'}>
                      {Number(product.price).toLocaleString()} ₸
                    </span>
                    <Badge 
                      variant={(product.botActive || product.bot_active) ? 'default' : 'outline'} 
                      className="ml-2 text-xs"
                    >
                      {(product.botActive || product.bot_active) ? 'Активен' : 'Пауза'}
                    </Badge>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {popoverProduct && triggerElement && (
        <PopoverSettings
          product={popoverProduct}
          onSave={handleSettingsSave}
          onClose={handlePopoverClose}
          triggerElement={triggerElement}
        />
      )}
    </>
  );
};

export default ProductList;
