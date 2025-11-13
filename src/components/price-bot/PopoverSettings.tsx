
import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { X } from "lucide-react";
import { Product } from "@/types";
import PriceBotSettings from "./PriceBotSettings";
import { usePositionCalculator, Position } from "./PositionCalculator";

interface PopoverSettingsProps {
  product: Product;
  onSave: (settings: any) => void;
  onClose: () => void;
  triggerElement: HTMLElement | null;
}

const PopoverSettings = ({ product, onSave, onClose, triggerElement }: PopoverSettingsProps) => {
  const popoverRef = useRef<HTMLDivElement>(null);
  const [position, setPosition] = useState<Position>({ top: 0, left: 0, placement: 'right' });

  useEffect(() => {
    if (!triggerElement || !popoverRef.current) return;

    const updatePosition = () => {
      const newPosition = usePositionCalculator(triggerElement, {
        popoverWidth: 400,
        popoverHeight: 500,
        offset: 16,
        preferredPlacement: 'right'
      });
      
      // Поднимаем popover выше на 60 пикселей
      const adjustedPosition = {
        ...newPosition,
        top: Math.max(20, newPosition.top - 60)
      };
      
      setPosition(adjustedPosition);
    };

    updatePosition();
    
    const handleScroll = () => updatePosition();
    const handleResize = () => updatePosition();
    
    window.addEventListener('scroll', handleScroll);
    window.addEventListener('resize', handleResize);
    
    return () => {
      window.removeEventListener('scroll', handleScroll);
      window.removeEventListener('resize', handleResize);
    };
  }, [triggerElement]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (popoverRef.current && !popoverRef.current.contains(event.target as Node)) {
        onClose();
      }
    };

    const handleEscapeKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleEscapeKey);

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscapeKey);
    };
  }, [onClose]);

  return createPortal(
    <div
      ref={popoverRef}
      className="fixed z-50 w-96 animate-in fade-in-0 zoom-in-95"
      style={{
        top: `${position.top}px`,
        left: `${position.left}px`,
      }}
    >
      {/* Стрелка, указывающая на товар */}
      {position.placement === 'right' && (
        <div className="absolute left-0 top-16 -translate-x-2 w-0 h-0 border-t-8 border-b-8 border-r-8 border-transparent border-r-white"></div>
      )}
      {position.placement === 'left' && (
        <div className="absolute right-0 top-16 translate-x-2 w-0 h-0 border-t-8 border-b-8 border-l-8 border-transparent border-l-white"></div>
      )}
      
      <Card className="shadow-lg border-2">
        <Tabs defaultValue="settings">
          <CardHeader className="pb-3">
            <div className="flex justify-between items-start gap-3">
              <div className="flex-1">
                <CardTitle className="text-base line-clamp-2 pr-2">
                  {product.name}
                </CardTitle>
                <Badge 
                  variant={(product.botActive || product.bot_active) ? 'default' : 'outline'}
                  className="mt-2"
                >
                  {(product.botActive || product.bot_active) ? 'Активен' : 'На паузе'}
                </Badge>
              </div>
              <button
                onClick={onClose}
                className="p-1 hover:bg-gray-100 rounded-full transition-colors flex-shrink-0"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <TabsList className="grid grid-cols-1 w-full">
              <TabsTrigger value="settings" className="text-sm">Настройки бота</TabsTrigger>
            </TabsList>
          </CardHeader>
          <CardContent className="pt-0">
            <TabsContent value="settings">
              <PriceBotSettings 
                product={product}
                onSave={onSave}
              />
            </TabsContent>
          </CardContent>
        </Tabs>
      </Card>
    </div>,
    document.body
  );
};

export default PopoverSettings;
