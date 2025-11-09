"use client";

import React from 'react';
import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from 'lucide-react';
import { Dropdown, DropdownItem } from './Dropdown';
import { Button } from './Button';

export interface TablePaginationProps {
  /** Current page (0-indexed) */
  currentPage: number;
  /** Total number of pages */
  totalPages: number;
  /** Total number of items */
  totalItems: number;
  /** Items per page */
  pageSize: number;
  /** Page size options */
  pageSizeOptions?: number[];
  /** Page change handler */
  onPageChange: (page: number) => void;
  /** Page size change handler */
  onPageSizeChange?: (pageSize: number) => void;
  /** Show page size selector */
  showPageSizeSelector?: boolean;
  /** Show total items */
  showTotal?: boolean;
  /** Show first/last buttons */
  showFirstLast?: boolean;
  /** Compact mode */
  compact?: boolean;
  /** Custom className */
  className?: string;
}

export const TablePagination: React.FC<TablePaginationProps> = ({
  currentPage,
  totalPages,
  totalItems,
  pageSize,
  pageSizeOptions = [10, 25, 50, 100],
  onPageChange,
  onPageSizeChange,
  showPageSizeSelector = true,
  showTotal = true,
  showFirstLast = true,
  compact = false,
  className = '',
}) => {
  // Ensure totalPages is valid before using it
  const safeTotalPages = isNaN(totalPages) || totalPages < 1 ? 1 : Math.max(1, Math.floor(totalPages));
  
  const handlePageChange = (newPage: number) => {
    if (newPage >= 0 && newPage < safeTotalPages) {
      onPageChange(newPage);
    }
  };

  const handlePageSizeChange = (value: string) => {
    if (onPageSizeChange) {
      onPageSizeChange(parseInt(value, 10));
      // Reset to first page when changing page size
      onPageChange(0);
    }
  };

  // Ensure currentPage is valid
  const safeCurrentPage = isNaN(currentPage) || currentPage < 0 ? 0 : Math.max(0, Math.min(currentPage, safeTotalPages - 1));
  
  const startItem = totalItems === 0 ? 0 : safeCurrentPage * pageSize + 1;
  const endItem = Math.min((safeCurrentPage + 1) * pageSize, totalItems);

  const pageSizeItems: DropdownItem[] = pageSizeOptions.map((size) => ({
    label: `${size} per page`,
    value: size.toString(),
  }));

  const isFirstPage = safeCurrentPage === 0;
  const isLastPage = safeCurrentPage >= safeTotalPages - 1;

  const getPageNumbers = () => {
    const pages: (number | 'ellipsis')[] = [];
    const maxVisible = compact ? 3 : 5;
    const halfVisible = Math.floor(maxVisible / 2);
    
    // Ensure totalPages is a valid number
    const safeTotalPages = isNaN(totalPages) || totalPages < 1 ? 1 : Math.max(1, Math.floor(totalPages));

    if (safeTotalPages <= maxVisible + 2) {
      // Show all pages if total is small
      for (let i = 0; i < safeTotalPages; i++) {
        pages.push(i);
      }
    } else {
      // Always show first page
      pages.push(0);

      let startPage = Math.max(1, currentPage - halfVisible);
      let endPage = Math.min(safeTotalPages - 2, currentPage + halfVisible);

      // Adjust if near start
      if (currentPage <= halfVisible) {
        endPage = maxVisible - 1;
      }

      // Adjust if near end
      if (currentPage >= safeTotalPages - halfVisible - 1) {
        startPage = safeTotalPages - maxVisible;
      }

      // Add ellipsis after first page if needed
      if (startPage > 1) {
        pages.push('ellipsis');
      }

      // Add middle pages
      for (let i = startPage; i <= endPage; i++) {
        pages.push(i);
      }

      // Add ellipsis before last page if needed
      if (endPage < safeTotalPages - 2) {
        pages.push('ellipsis');
      }

      // Always show last page
      pages.push(safeTotalPages - 1);
    }

    return pages;
  };

  const containerClasses = [
    'flex items-center justify-between gap-4',
    'flex-wrap',
    className,
  ].filter(Boolean).join(' ');

  return (
    <div className={containerClasses}>
      {/* Left side - Total and Page Size */}
      <div className="flex items-center gap-4 flex-wrap">
        {showTotal && (
          <div className="text-sm text-gray-700">
            Showing <span className="font-medium">{startItem}</span> to{' '}
            <span className="font-medium">{endItem}</span> of{' '}
            <span className="font-medium">{totalItems}</span> results
          </div>
        )}

        {showPageSizeSelector && onPageSizeChange && (
          <Dropdown
            trigger={
              <span className="text-sm">
                {pageSize} per page
              </span>
            }
            items={pageSizeItems}
            value={pageSize.toString()}
            onChange={handlePageSizeChange}
            width="auto"
          />
        )}
      </div>

      {/* Right side - Navigation */}
      <nav
        className="flex items-center gap-1"
        aria-label="Pagination"
        role="navigation"
      >
        {showFirstLast && (
          <Button
            variant="ghost"
            size={compact ? 'sm' : 'md'}
            onClick={() => handlePageChange(0)}
            disabled={isFirstPage}
            aria-label="First page"
          >
            <ChevronsLeft className="w-4 h-4" />
          </Button>
        )}

        <Button
          variant="ghost"
          size={compact ? 'sm' : 'md'}
          onClick={() => handlePageChange(currentPage - 1)}
          disabled={isFirstPage}
          aria-label="Previous page"
        >
          <ChevronLeft className="w-4 h-4" />
        </Button>

        {/* Page Numbers */}
        <div className="hidden sm:flex items-center gap-1">
          {getPageNumbers().map((page, index) => {
            if (page === 'ellipsis') {
              return (
                <span
                  key={`ellipsis-${index}`}
                  className="px-2 text-gray-400"
                  aria-hidden="true"
                >
                  ...
                </span>
              );
            }

            return (
              <button
                key={page}
                onClick={() => handlePageChange(page)}
                className={`
                  ${compact ? 'px-2 py-1 text-sm' : 'px-3 py-2 text-sm'}
                  rounded-md font-medium transition-colors
                  ${
                    safeCurrentPage === page
                      ? 'bg-primary-600 text-white'
                      : 'text-gray-700 hover:bg-gray-100'
                  }
                `}
                aria-label={`Page ${page + 1}`}
                aria-current={safeCurrentPage === page ? 'page' : undefined}
              >
                {page + 1}
              </button>
            );
          })}
        </div>

        {/* Mobile page indicator */}
        <div className="sm:hidden px-3 py-1 text-sm text-gray-700">
          Page {safeCurrentPage + 1} of {safeTotalPages}
        </div>

        <Button
          variant="ghost"
          size={compact ? 'sm' : 'md'}
          onClick={() => handlePageChange(safeCurrentPage + 1)}
          disabled={isLastPage}
          aria-label="Next page"
        >
          <ChevronRight className="w-4 h-4" />
        </Button>

        {showFirstLast && (
          <Button
            variant="ghost"
            size={compact ? 'sm' : 'md'}
            onClick={() => handlePageChange(safeTotalPages - 1)}
            disabled={isLastPage}
            aria-label="Last page"
          >
            <ChevronsRight className="w-4 h-4" />
          </Button>
        )}
      </nav>
    </div>
  );
};

// Simple pagination hook
export const usePagination = (
  totalItems: number,
  initialPageSize: number = 10
) => {
  const [currentPage, setCurrentPage] = React.useState(0);
  const [pageSize, setPageSize] = React.useState(initialPageSize);

  const totalPages = Math.ceil(totalItems / pageSize);

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  const handlePageSizeChange = (newPageSize: number) => {
    setPageSize(newPageSize);
    setCurrentPage(0);
  };

  const startIndex = currentPage * pageSize;
  const endIndex = Math.min(startIndex + pageSize, totalItems);

  return {
    currentPage,
    pageSize,
    totalPages,
    startIndex,
    endIndex,
    handlePageChange,
    handlePageSizeChange,
  };
};
