
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination";

interface ProductsPaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

const ProductsPagination = ({ currentPage, totalPages, onPageChange }: ProductsPaginationProps) => {
  if (totalPages <= 1) return null;

  const getVisiblePages = () => {
    const pages = [];
    
    if (totalPages <= 7) {
      // Show all pages if 7 or fewer
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      // Always show first page
      pages.push(1);
      
      if (currentPage <= 4) {
        // Beginning: 1, 2, 3, 4, 5, ..., last
        pages.push(2, 3, 4, 5);
        pages.push('ellipsis');
        pages.push(totalPages);
      } else if (currentPage >= totalPages - 3) {
        // End: 1, ..., last-4, last-3, last-2, last-1, last
        pages.push('ellipsis');
        for (let i = totalPages - 4; i <= totalPages; i++) {
          if (i > 1) pages.push(i);
        }
      } else {
        // Middle: 1, ..., current-1, current, current+1, ..., last
        pages.push('ellipsis');
        pages.push(currentPage - 1, currentPage, currentPage + 1);
        pages.push('ellipsis');
        pages.push(totalPages);
      }
    }
    
    return pages;
  };

  const visiblePages = getVisiblePages();

  return (
    <div className="flex justify-center mt-6">
      <Pagination>
        <PaginationContent className="gap-1">
          <PaginationItem>
            <PaginationPrevious 
              onClick={() => currentPage > 1 && onPageChange(currentPage - 1)}
              className={currentPage <= 1 ? "pointer-events-none opacity-50" : "cursor-pointer"}
            />
          </PaginationItem>
          
          {visiblePages.map((page, index) => (
            <PaginationItem key={index}>
              {page === 'ellipsis' ? (
                <PaginationEllipsis />
              ) : (
                <PaginationLink 
                  onClick={() => onPageChange(page as number)}
                  isActive={currentPage === page}
                  className="cursor-pointer min-w-[40px] text-center"
                >
                  {page}
                </PaginationLink>
              )}
            </PaginationItem>
          ))}
          
          <PaginationItem>
            <PaginationNext 
              onClick={() => currentPage < totalPages && onPageChange(currentPage + 1)}
              className={currentPage >= totalPages ? "pointer-events-none opacity-50" : "cursor-pointer"}
            />
          </PaginationItem>
        </PaginationContent>
      </Pagination>
    </div>
  );
};

export default ProductsPagination;
