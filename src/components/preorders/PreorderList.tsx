
import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  Pagination, 
  PaginationContent, 
  PaginationItem, 
  PaginationLink, 
  PaginationNext, 
  PaginationPrevious 
} from "@/components/ui/pagination";
import { Clock, CheckCircle, Package, MapPin, Calendar, Timer } from "lucide-react";
import { toast } from "sonner";

export interface PreorderItem {
  id: string;
  article: string;
  name: string;
  brand: string;
  price: number;
  warehouses: number[];
  deliveryDays: number;
  status: "processing" | "added";
  createdAt: Date;
}

interface PreorderListProps {
  items: PreorderItem[];
  onResubmit: (id: string) => void;
}

const ITEMS_PER_PAGE = 10;

const PreorderList = ({ items, onResubmit }: PreorderListProps) => {
  const [currentPage, setCurrentPage] = useState(1);

  const totalPages = Math.ceil(items.length / ITEMS_PER_PAGE);
  const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
  const endIndex = startIndex + ITEMS_PER_PAGE;
  const currentItems = items.slice(startIndex, endIndex);

  const getStatusConfig = (status: PreorderItem["status"]) => {
    switch (status) {
      case "processing":
        return {
          label: "В обработке",
          icon: Clock,
          className: "bg-amber-100 dark:bg-amber-900/30 text-amber-800 dark:text-amber-200 border-amber-300 dark:border-amber-700"
        };
      case "added":
        return {
          label: "Активен в каталоге",
          icon: CheckCircle,
          className: "bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200 border-green-300 dark:border-green-700"
        };
      default:
        return {
          label: status,
          icon: Clock,
          className: "bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200 border-gray-300 dark:border-gray-600"
        };
    }
  };

  const handleResubmit = (id: string) => {
    onResubmit(id);
    toast.success("Товар отправлен на повторную обработку");
  };

  const renderProductCard = (item: PreorderItem) => {
    const statusConfig = getStatusConfig(item.status);
    const StatusIcon = statusConfig.icon;

    return (
      <Card key={item.id} className="p-4 space-y-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <h3 className="font-medium text-gray-900 dark:text-white">{item.name}</h3>
              <div className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium border ${statusConfig.className}`}>
                <StatusIcon className="h-3 w-3" />
                {statusConfig.label}
              </div>
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">
              <p><span className="font-medium">Артикул:</span> {item.article}</p>
              {item.brand && <p><span className="font-medium">Бренд:</span> {item.brand}</p>}
            </div>
          </div>
          <div className="text-right">
            <div className="font-semibold text-gray-900 dark:text-white">
              {item.price.toLocaleString()} ₸
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-400">
              {item.createdAt.toLocaleDateString('ru-RU')}
            </div>
          </div>
        </div>
        
        <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400 pt-2 border-t border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-1">
            <MapPin className="h-3 w-3" />
            <span>Склады: {item.warehouses.join(', ')}</span>
          </div>
          <div className="flex items-center gap-1">
            <Package className="h-3 w-3" />
            <span>Доставка: {item.deliveryDays} дн.</span>
          </div>
        </div>
      </Card>
    );
  };

  if (items.length === 0) {
    return (
      <div className="text-center py-8">
        <Package className="h-12 w-12 text-gray-400 dark:text-gray-500 mx-auto mb-3" />
        <h3 className="font-medium text-gray-600 dark:text-gray-300 mb-1">
          Заявок пока нет
        </h3>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Создайте первую заявку на добавление товара
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {currentItems.map(renderProductCard)}
      
      {totalPages > 1 && (
        <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
          <Pagination>
            <PaginationContent>
              <PaginationItem>
                <PaginationPrevious 
                  onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                  className={currentPage === 1 ? "pointer-events-none opacity-50" : "cursor-pointer"}
                />
              </PaginationItem>
              
              {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
                <PaginationItem key={page}>
                  <PaginationLink
                    onClick={() => setCurrentPage(page)}
                    isActive={currentPage === page}
                    className="cursor-pointer"
                  >
                    {page}
                  </PaginationLink>
                </PaginationItem>
              ))}
              
              <PaginationItem>
                <PaginationNext 
                  onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                  className={currentPage === totalPages ? "pointer-events-none opacity-50" : "cursor-pointer"}
                />
              </PaginationItem>
            </PaginationContent>
          </Pagination>
        </div>
      )}
    </div>
  );
};

export default PreorderList;
