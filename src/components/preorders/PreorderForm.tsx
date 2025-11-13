
import { useState } from "react";
import { useForm, useFieldArray } from "react-hook-form";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Plus, Trash2, X } from "lucide-react";
import { toast } from "sonner";

interface PreorderProduct {
  article: string;
  name: string;
  brand: string;
  price: number;
  warehouse1: boolean;
  warehouse2: boolean;
  warehouse3: boolean;
  warehouse4: boolean;
  warehouse5: boolean;
  deliveryDays: number;
}

interface PreorderFormData {
  products: PreorderProduct[];
}

interface PreorderFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (products: PreorderProduct[]) => void;
}

const PreorderForm = ({ isOpen, onClose, onSubmit }: PreorderFormProps) => {
  const { control, handleSubmit, watch, formState: { errors } } = useForm<PreorderFormData>({
    defaultValues: {
      products: [{
        article: "",
        name: "",
        brand: "",
        price: 0,
        warehouse1: false,
        warehouse2: false,
        warehouse3: false,
        warehouse4: false,
        warehouse5: false,
        deliveryDays: 1
      }]
    }
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: "products"
  });

  const watchedProducts = watch("products");

  const validateWarehouses = (index: number) => {
    const product = watchedProducts[index];
    return product.warehouse1 || product.warehouse2 || product.warehouse3 || product.warehouse4 || product.warehouse5;
  };

  const onFormSubmit = (data: PreorderFormData) => {
    // Validate that each product has at least one warehouse selected
    for (let i = 0; i < data.products.length; i++) {
      if (!validateWarehouses(i)) {
        toast.error(`Товар ${i + 1}: выберите хотя бы один склад`);
        return;
      }
    }

    onSubmit(data.products);
    onClose();
    toast.success(`Создано ${data.products.length} заявок на товары`);
  };

  const addProduct = () => {
    append({
      article: "",
      name: "",
      brand: "",
      price: 0,
      warehouse1: false,
      warehouse2: false,
      warehouse3: false,
      warehouse4: false,
      warehouse5: false,
      deliveryDays: 1
    });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />
      
      <div className="relative mx-4 max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <Card className="p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Добавить заявку на товар</h2>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>

        <form onSubmit={handleSubmit(onFormSubmit)} className="space-y-6">
          {fields.map((field, index) => (
            <Card key={field.id} className="p-4">
              <div className="flex justify-between items-center mb-4">
                <h3 className="font-medium text-gray-900 dark:text-white">Товар {index + 1}</h3>
                {fields.length > 1 && (
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    onClick={() => remove(index)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                )}
              </div>
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor={`article-${index}`} className="text-sm font-medium text-gray-900 dark:text-white mb-2 block">Артикул *</Label>
                    <Input
                      id={`article-${index}`}
                      {...control.register(`products.${index}.article`, { required: "Артикул обязателен" })}
                      placeholder="Введите артикул"
                    />
                    {errors.products?.[index]?.article && (
                      <p className="text-sm text-red-500 mt-1">{errors.products[index]?.article?.message}</p>
                    )}
                  </div>

                  <div>
                    <Label htmlFor={`name-${index}`} className="text-sm font-medium text-gray-900 dark:text-white mb-2 block">Название товара *</Label>
                    <Input
                      id={`name-${index}`}
                      {...control.register(`products.${index}.name`, { required: "Название обязательно" })}
                      placeholder="Введите название товара"
                    />
                    {errors.products?.[index]?.name && (
                      <p className="text-sm text-red-500 mt-1">{errors.products[index]?.name?.message}</p>
                    )}
                  </div>

                  <div>
                    <Label htmlFor={`brand-${index}`} className="text-sm font-medium text-gray-900 dark:text-white mb-2 block">Бренд</Label>
                    <Input
                      id={`brand-${index}`}
                      {...control.register(`products.${index}.brand`)}
                      placeholder="Введите бренд (необязательно)"
                    />
                  </div>

                  <div>
                    <Label htmlFor={`price-${index}`} className="text-sm font-medium text-gray-900 dark:text-white mb-2 block">Цена *</Label>
                    <Input
                      id={`price-${index}`}
                      type="number"
                      step="0.01"
                      {...control.register(`products.${index}.price`, { 
                        required: "Цена обязательна",
                        min: { value: 0.01, message: "Цена должна быть больше 0" }
                      })}
                      placeholder="0.00"
                    />
                    {errors.products?.[index]?.price && (
                      <p className="text-sm text-red-500 mt-1">{errors.products[index]?.price?.message}</p>
                    )}
                  </div>

                  <div>
                    <Label htmlFor={`deliveryDays-${index}`} className="text-sm font-medium text-gray-900 dark:text-white mb-2 block">Срок доставки (дни) *</Label>
                    <Input
                      id={`deliveryDays-${index}`}
                      type="number"
                      {...control.register(`products.${index}.deliveryDays`, { 
                        required: "Срок доставки обязателен",
                        min: { value: 1, message: "Минимум 1 день" }
                      })}
                      placeholder="1"
                    />
                    {errors.products?.[index]?.deliveryDays && (
                      <p className="text-sm text-red-500 mt-1">{errors.products[index]?.deliveryDays?.message}</p>
                    )}
                  </div>
                </div>

                <div>
                  <Label className="text-sm font-medium text-gray-900 dark:text-white mb-2 block">Склады *</Label>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    {[1, 2, 3, 4, 5].map((warehouseNum) => (
                      <div key={warehouseNum} className="flex items-center space-x-2">
                        <Checkbox
                          id={`warehouse${warehouseNum}-${index}`}
                          {...control.register(`products.${index}.warehouse${warehouseNum}` as any)}
                        />
                        <Label htmlFor={`warehouse${warehouseNum}-${index}`} className="text-sm text-gray-900 dark:text-white">
                          Склад {warehouseNum}
                        </Label>
                      </div>
                    ))}
                  </div>
                  {!validateWarehouses(index) && watchedProducts[index] && (
                    <p className="text-sm text-red-500 mt-1">Выберите хотя бы один склад</p>
                  )}
                </div>
              </div>
            </Card>
          ))}

          <div className="flex justify-between items-center pt-4 border-t border-gray-200 dark:border-gray-700">
            <Button
              type="button"
              variant="outline"
              onClick={addProduct}
              className="flex items-center gap-2"
            >
              <Plus className="h-4 w-4" />
              Добавить товар
            </Button>

            <div className="flex gap-3">
              <Button type="button" variant="outline" onClick={onClose}>
                Отмена
              </Button>
              <Button type="submit">
                Создать заявку
              </Button>
            </div>
          </div>
        </form>
        </Card>
      </div>
    </div>
  );
};

export default PreorderForm;
