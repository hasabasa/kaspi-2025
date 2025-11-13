
import { useState } from "react";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectGroup, SelectItem, SelectLabel, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card } from "@/components/ui/card";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { ExternalLink } from "lucide-react";

interface UnitEconomicsFormProps {
  data: {
    costPrice: number;
    sellingPrice: number;
    category: string;
    weight: number;
    deliveryScope: string;
    paymentType: string;
  };
  onChange: (data: any) => void;
}

const UnitEconomicsForm = ({ data, onChange }: UnitEconomicsFormProps) => {
  const handleInputChange = (field: string, value: any) => {
    onChange({ ...data, [field]: value });
  };

  const categories = [
    "Автотовары", "Аксессуары", "Аптека", "Бытовая техника",
    "Детские товары", "Книги/Досуг", "Канцелярия", "Компьютеры",
    "Красота и здоровье", "Мебель", "Обувь", "Одежда",
    "Продукты", "ТВ, Аудио, Видео", "Телефоны", "Дом и дача",
    "Животные", "Украшения", "Электроника", "Косметика", "Ремонт", "Спорт"
  ];

  return (
    <div className="space-y-6">
      {/* Простая форма без цветных блоков */}
      <div className="space-y-4">
        <div>
          <Label htmlFor="costPrice" className="text-sm font-medium text-gray-900 dark:text-white mb-2 block">
            Себестоимость (₸)
          </Label>
          <Input
            id="costPrice"
            type="number"
            value={data.costPrice}
            onChange={(e) => handleInputChange("costPrice", Number(e.target.value))}
            placeholder="0"
          />
        </div>

        <div>
          <Label htmlFor="sellingPrice" className="text-sm font-medium text-gray-900 dark:text-white mb-2 block">
            Цена продажи (₸)
          </Label>
          <Input
            id="sellingPrice"
            type="number"
            value={data.sellingPrice}
            onChange={(e) => handleInputChange("sellingPrice", Number(e.target.value))}
            placeholder="0"
          />
        </div>

        <div>
          <Label htmlFor="category" className="text-sm font-medium text-gray-900 dark:text-white mb-2 block">
            Категория товара
          </Label>
          <Select 
            value={data.category} 
            onValueChange={(value) => handleInputChange("category", value)}
          >
            <SelectTrigger id="category">
              <SelectValue placeholder="Выберите категорию" />
            </SelectTrigger>
            <SelectContent>
              <SelectGroup>
                <SelectLabel>Категории</SelectLabel>
                {categories.map((category) => (
                  <SelectItem key={category} value={category}>
                    {category}
                  </SelectItem>
                ))}
              </SelectGroup>
            </SelectContent>
          </Select>
        </div>

        <div>
          <Label htmlFor="weight" className="text-sm font-medium text-gray-900 dark:text-white mb-2 block">
            Вес товара (кг)
          </Label>
          <Input
            id="weight"
            type="number"
            min="0.1"
            step="0.1"
            value={data.weight}
            onChange={(e) => handleInputChange("weight", Number(e.target.value))}
            placeholder="1.0"
          />
        </div>

        <div>
          <Label htmlFor="deliveryScope" className="text-sm font-medium text-gray-900 dark:text-white mb-2 block">
            Зона доставки
          </Label>
          <Select 
            value={data.deliveryScope} 
            onValueChange={(value) => handleInputChange("deliveryScope", value)}
          >
            <SelectTrigger id="deliveryScope">
              <SelectValue placeholder="Выберите зону" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="По городу">По городу</SelectItem>
              <SelectItem value="По Казахстану">По Казахстану</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div>
          <Label htmlFor="paymentType" className="text-sm font-medium text-gray-900 dark:text-white mb-2 block">
            Тип оплаты
          </Label>
          <Select 
            value={data.paymentType} 
            onValueChange={(value) => handleInputChange("paymentType", value)}
          >
            <SelectTrigger id="paymentType">
              <SelectValue placeholder="Выберите тип" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="Gold">Gold (обычная оплата)</SelectItem>
              <SelectItem value="Red">Kaspi Red</SelectItem>
              <SelectItem value="Kredit">Kaspi Kredit</SelectItem>
              <SelectItem value="Installment">Рассрочка 0-0-12 / 0-0-24</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Простая ссылка на тарифы */}
      <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
        <button
          onClick={() => window.open('https://guide.kaspi.kz/partner/ru/shop/conditions/commissions', '_blank')}
          className="inline-flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
        >
          <span>Официальные тарифы Kaspi.kz</span>
          <ExternalLink className="h-3 w-3" />
        </button>
      </div>
    </div>
  );
};

export default UnitEconomicsForm;
