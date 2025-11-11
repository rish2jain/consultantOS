"use client";

import React from 'react';
import { Spinner } from './Spinner';

export interface Column<T> {
  /** Column unique identifier */
  key: string;
  /** Column header label */
  label: string;
  /** Sort key (if different from key) */
  sortKey?: string;
  /** Whether column is sortable */
  sortable?: boolean;
  /** Whether column is filterable */
  filterable?: boolean;
  /** Filter type */
  filterType?: 'text' | 'select' | 'date' | 'dateRange';
  /** Filter options for select type */
  filterOptions?: Array<{ label: string; value: string }>;
  /** Custom cell renderer */
  render?: (value: any, row: T, index: number) => React.ReactNode;
  /** Cell accessor function */
  accessor?: (row: T) => any;
  /** Column width */
  width?: string;
  /** Column alignment */
  align?: 'left' | 'center' | 'right';
  /** Hide on mobile */
  hideOnMobile?: boolean;
}

export interface DataTableProps<T> {
  /** Table columns */
  columns: Column<T>[];
  /** Table data */
  data: T[];
  /** Unique row key accessor */
  rowKey: (row: T, index: number) => string | number;
  /** Loading state */
  isLoading?: boolean;
  /** Empty state message */
  emptyMessage?: string;
  /** Empty state component */
  emptyComponent?: React.ReactNode;
  /** Row selection mode */
  selectionMode?: 'none' | 'single' | 'multi';
  /** Selected row keys */
  selectedRows?: Set<string | number>;
  /** Selection change handler */
  onSelectionChange?: (selectedKeys: Set<string | number>) => void;
  /** Row click handler */
  onRowClick?: (row: T, index: number) => void;
  /** Hover effect on rows */
  hoverable?: boolean;
  /** Striped rows */
  striped?: boolean;
  /** Bordered table */
  bordered?: boolean;
  /** Compact table */
  compact?: boolean;
  /** Custom row className */
  rowClassName?: (row: T, index: number) => string;
  /** Sticky header */
  stickyHeader?: boolean;
  /** Max height for scrolling */
  maxHeight?: string;
  /** Custom className */
  className?: string;
}

export function DataTable<T>({
  columns,
  data,
  rowKey,
  isLoading = false,
  emptyMessage = 'No data available',
  emptyComponent,
  selectionMode = 'none',
  selectedRows = new Set(),
  onSelectionChange,
  onRowClick,
  hoverable = true,
  striped = false,
  bordered = false,
  compact = false,
  rowClassName,
  stickyHeader = false,
  maxHeight,
  className = '',
}: DataTableProps<T>) {
  const handleSelectAll = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (!onSelectionChange) return;

    if (event.target.checked) {
      const allKeys = new Set(data.map((row, index) => rowKey(row, index)));
      onSelectionChange(allKeys);
    } else {
      onSelectionChange(new Set());
    }
  };

  const handleSelectRow = (key: string | number, event: React.ChangeEvent<HTMLInputElement>) => {
    if (!onSelectionChange) return;

    const newSelection = new Set(selectedRows);
    if (event.target.checked) {
      if (selectionMode === 'single') {
        newSelection.clear();
      }
      newSelection.add(key);
    } else {
      newSelection.delete(key);
    }
    onSelectionChange(newSelection);
  };

  const getCellValue = (row: T, column: Column<T>) => {
    if (column.accessor) {
      return column.accessor(row);
    }
    return (row as any)[column.key];
  };

  const renderCell = (row: T, column: Column<T>, index: number) => {
    const value = getCellValue(row, column);

    if (column.render) {
      return column.render(value, row, index);
    }

    return value ?? '-';
  };

  const allSelected = data.length > 0 && selectedRows.size === data.length;
  const someSelected = selectedRows.size > 0 && selectedRows.size < data.length;

  const tableClasses = [
    'w-full',
    bordered ? 'border border-gray-200' : '',
    className,
  ].filter(Boolean).join(' ');

  const containerClasses = [
    'relative overflow-x-auto',
    maxHeight ? 'overflow-y-auto' : '',
    bordered ? 'rounded-lg' : '',
  ].filter(Boolean).join(' ');

  return (
    <div className={containerClasses} style={{ maxHeight }}>
      <table className={tableClasses}>
        <thead
          className={`
            bg-gray-50 border-b border-gray-200
            ${stickyHeader ? 'sticky top-0 z-10' : ''}
          `}
        >
          <tr>
            {selectionMode !== 'none' && (
              <th
                className={`
                  text-left font-medium text-black
                  ${compact ? 'px-3 py-2' : 'px-6 py-3'}
                `}
                style={{ width: '48px', color: '#000000' }}
              >
                {selectionMode === 'multi' && (
                  <input
                    type="checkbox"
                    checked={allSelected}
                    ref={(input) => {
                      if (input) {
                        input.indeterminate = someSelected;
                      }
                    }}
                    onChange={handleSelectAll}
                    className="w-4 h-4 text-primary-600 rounded border-gray-300 focus:ring-primary-500"
                    aria-label="Select all rows"
                  />
                )}
              </th>
            )}
            {columns.map((column) => (
              <th
                key={column.key}
                className={`
                  text-left text-xs font-semibold text-black uppercase tracking-wider
                  ${compact ? 'px-3 py-2' : 'px-6 py-3'}
                  ${column.align === 'center' ? 'text-center' : ''}
                  ${column.align === 'right' ? 'text-right' : ''}
                  ${column.hideOnMobile ? 'hidden md:table-cell' : ''}
                `}
                style={{ width: column.width, color: '#000000' }}
              >
                {column.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200" style={{ backgroundColor: '#ffffff' }}>
          {isLoading ? (
            <tr key="loading-row">
              <td
                colSpan={columns.length + (selectionMode !== 'none' ? 1 : 0)}
                className="px-6 py-12 text-center"
              >
                <div className="flex flex-col items-center justify-center gap-3">
                  <Spinner size="lg" />
                  <span className="text-sm text-gray-500">Loading data...</span>
                </div>
              </td>
            </tr>
          ) : data.length === 0 ? (
            <tr key="empty-row">
              <td
                colSpan={columns.length + (selectionMode !== 'none' ? 1 : 0)}
                className="px-6 py-12 text-center"
              >
                {emptyComponent || (
                  <div className="flex flex-col items-center justify-center gap-2">
                    <svg
                      className="w-12 h-12 text-gray-300"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={1.5}
                        d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
                      />
                    </svg>
                    <p className="text-sm text-gray-500">{emptyMessage}</p>
                  </div>
                )}
              </td>
            </tr>
          ) : (
            data.map((row, index) => {
              const key = rowKey(row, index);
              const isSelected = selectedRows.has(key);
              const customClassName = rowClassName?.(row, index) || '';

              return (
                <tr
                  key={key}
                  onClick={onRowClick ? () => onRowClick(row, index) : undefined}
                  className={`
                    ${striped && index % 2 === 0 ? 'bg-gray-50' : 'bg-white'}
                    ${hoverable ? 'hover:bg-gray-50 transition-colors' : ''}
                    ${isSelected ? 'bg-primary-50' : ''}
                    ${onRowClick ? 'cursor-pointer' : ''}
                    ${customClassName}
                  `}
                  style={{ 
                    backgroundColor: striped && index % 2 === 0 ? '#f9fafb' : '#ffffff'
                  }}
                >
                  {selectionMode !== 'none' && (
                    <td className={compact ? 'px-3 py-2' : 'px-6 py-4'}>
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={(e) => handleSelectRow(key, e)}
                        onClick={(e) => e.stopPropagation()}
                        className="w-4 h-4 text-primary-600 rounded border-gray-300 focus:ring-primary-500"
                        aria-label={`Select row ${index + 1}`}
                      />
                    </td>
                  )}
                  {columns.map((column) => (
                    <td
                      key={`${key}-${column.key}`}
                      onClick={onRowClick ? (e) => {
                        // Allow clicks on interactive elements to work, but also trigger row click
                        const target = e.target as HTMLElement;
                        if (target.tagName === 'BUTTON' || target.tagName === 'A' || target.closest('button, a')) {
                          return; // Don't trigger row click for buttons/links
                        }
                        onRowClick(row, index);
                      } : undefined}
                      className={`
                        text-sm font-medium text-black
                        ${compact ? 'px-3 py-2' : 'px-6 py-4'}
                        ${column.align === 'center' ? 'text-center' : ''}
                        ${column.align === 'right' ? 'text-right' : ''}
                        ${column.hideOnMobile ? 'hidden md:table-cell' : ''}
                        ${onRowClick ? 'cursor-pointer' : ''}
                      `}
                      style={{ color: '#000000' }}
                    >
                      {renderCell(row, column, index)}
                    </td>
                  ))}
                </tr>
              );
            })
          )}
        </tbody>
      </table>
    </div>
  );
}

// Loading skeleton for DataTable
export interface DataTableSkeletonProps {
  columns: number;
  rows?: number;
  compact?: boolean;
}

export const DataTableSkeleton: React.FC<DataTableSkeletonProps> = ({
  columns,
  rows = 5,
  compact = false,
}) => {
  return (
    <div className="w-full overflow-x-auto">
      <table className="w-full">
        <thead className="bg-gray-50 border-b border-gray-200">
          <tr>
            {Array.from({ length: columns }).map((_, i) => (
              <th
                key={i}
                className={`text-black ${compact ? 'px-3 py-2' : 'px-6 py-3'}`}
                style={{ color: '#000000' }}
              >
                <div className="h-4 bg-gray-200 rounded animate-pulse" />
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {Array.from({ length: rows }).map((_, rowIndex) => (
            <tr key={rowIndex}>
              {Array.from({ length: columns }).map((_, colIndex) => (
                <td
                  key={colIndex}
                  className={compact ? 'px-3 py-2' : 'px-6 py-4'}
                >
                  <div className="h-4 bg-gray-100 rounded animate-pulse" />
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
