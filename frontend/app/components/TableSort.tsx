"use client";

import React from 'react';
import { ArrowUp, ArrowDown, ArrowUpDown } from 'lucide-react';

export type SortDirection = 'asc' | 'desc' | null;

export interface SortConfig {
  /** Column key being sorted */
  key: string;
  /** Sort direction */
  direction: SortDirection;
}

export interface TableSortProps {
  /** Column key */
  columnKey: string;
  /** Column label */
  label: string;
  /** Current sort configuration */
  sortConfig?: SortConfig;
  /** Sort change handler */
  onSort: (key: string) => void;
  /** Custom className */
  className?: string;
  /** Align */
  align?: 'left' | 'center' | 'right';
}

export const TableSort: React.FC<TableSortProps> = ({
  columnKey,
  label,
  sortConfig,
  onSort,
  className = '',
  align = 'left',
}) => {
  const isSorted = sortConfig?.key === columnKey;
  const direction = isSorted ? sortConfig.direction : null;

  const handleClick = () => {
    onSort(columnKey);
  };

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      onSort(columnKey);
    }
  };

  const alignClasses = {
    left: 'justify-start',
    center: 'justify-center',
    right: 'justify-end',
  };

  return (
    <button
      type="button"
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      className={`
        group flex items-center gap-2 w-full
        ${alignClasses[align]}
        text-xs font-medium text-gray-700 uppercase tracking-wider
        hover:text-gray-900 transition-colors
        focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 rounded
        ${className}
      `}
      aria-label={`Sort by ${label} ${
        direction === 'asc'
          ? 'descending'
          : direction === 'desc'
          ? 'unsort'
          : 'ascending'
      }`}
      aria-sort={
        direction === 'asc'
          ? 'ascending'
          : direction === 'desc'
          ? 'descending'
          : 'none'
      }
    >
      <span>{label}</span>
      <span className="flex-shrink-0">
        {direction === 'asc' ? (
          <ArrowUp className="w-4 h-4 text-primary-600" aria-hidden="true" />
        ) : direction === 'desc' ? (
          <ArrowDown className="w-4 h-4 text-primary-600" aria-hidden="true" />
        ) : (
          <ArrowUpDown
            className="w-4 h-4 text-gray-400 group-hover:text-gray-600 transition-colors"
            aria-hidden="true"
          />
        )}
      </span>
    </button>
  );
};

// Hook for managing table sorting
export interface UseSortOptions<T> {
  /** Initial sort configuration */
  initialSort?: SortConfig;
  /** Custom sort functions by column key */
  customSorters?: Record<string, (a: T, b: T) => number>;
}

export const useSort = <T,>(options: UseSortOptions<T> = {}) => {
  const [sortConfig, setSortConfig] = React.useState<SortConfig>(
    options.initialSort || { key: '', direction: null }
  );

  const handleSort = (key: string) => {
    setSortConfig((prevConfig) => {
      if (prevConfig.key !== key) {
        // New column - sort ascending
        return { key, direction: 'asc' };
      }

      // Same column - cycle through asc -> desc -> null
      if (prevConfig.direction === 'asc') {
        return { key, direction: 'desc' };
      } else if (prevConfig.direction === 'desc') {
        return { key: '', direction: null };
      } else {
        return { key, direction: 'asc' };
      }
    });
  };

  const sortData = (data: T[]): T[] => {
    if (!sortConfig.key || !sortConfig.direction) {
      return data;
    }

    const sorted = [...data].sort((a, b) => {
      // Use custom sorter if provided
      if (options.customSorters?.[sortConfig.key]) {
        const result = options.customSorters[sortConfig.key](a, b);
        return sortConfig.direction === 'asc' ? result : -result;
      }

      // Default sorting
      const aValue = (a as any)[sortConfig.key];
      const bValue = (b as any)[sortConfig.key];

      if (aValue === bValue) return 0;

      // Handle null/undefined
      if (aValue == null) return 1;
      if (bValue == null) return -1;

      // String comparison
      if (typeof aValue === 'string' && typeof bValue === 'string') {
        const result = aValue.localeCompare(bValue, undefined, {
          numeric: true,
          sensitivity: 'base',
        });
        return sortConfig.direction === 'asc' ? result : -result;
      }

      // Number/Date comparison
      if (aValue < bValue) {
        return sortConfig.direction === 'asc' ? -1 : 1;
      }
      if (aValue > bValue) {
        return sortConfig.direction === 'asc' ? 1 : -1;
      }

      return 0;
    });

    return sorted;
  };

  return {
    sortConfig,
    handleSort,
    sortData,
  };
};

// Multi-column sort support
export interface MultiSortConfig {
  key: string;
  direction: SortDirection;
  priority: number;
}

export const useMultiSort = <T,>(
  options: UseSortOptions<T> = {}
) => {
  const [sortConfigs, setSortConfigs] = React.useState<MultiSortConfig[]>([]);

  const handleSort = (key: string, additive: boolean = false) => {
    setSortConfigs((prevConfigs) => {
      if (!additive) {
        // Single column sort - replace all
        const existing = prevConfigs.find((c) => c.key === key);
        if (!existing) {
          return [{ key, direction: 'asc', priority: 0 }];
        }
        if (existing.direction === 'asc') {
          return [{ key, direction: 'desc', priority: 0 }];
        }
        return [];
      }

      // Multi-column sort - add or update
      const existingIndex = prevConfigs.findIndex((c) => c.key === key);
      if (existingIndex === -1) {
        // Add new column
        return [
          ...prevConfigs,
          { key, direction: 'asc', priority: prevConfigs.length },
        ];
      }

      // Update existing column
      const updated = [...prevConfigs];
      const existing = updated[existingIndex];
      if (existing.direction === 'asc') {
        updated[existingIndex] = { ...existing, direction: 'desc' };
      } else {
        // Remove this sort
        updated.splice(existingIndex, 1);
        // Update priorities
        updated.forEach((config, index) => {
          config.priority = index;
        });
      }
      return updated;
    });
  };

  const sortData = (data: T[]): T[] => {
    if (sortConfigs.length === 0) {
      return data;
    }

    return [...data].sort((a, b) => {
      for (const config of sortConfigs) {
        // Use custom sorter if provided
        if (options.customSorters?.[config.key]) {
          const result = options.customSorters[config.key](a, b);
          if (result !== 0) {
            return config.direction === 'asc' ? result : -result;
          }
          continue;
        }

        // Default sorting
        const aValue = (a as any)[config.key];
        const bValue = (b as any)[config.key];

        if (aValue === bValue) continue;

        // Handle null/undefined
        if (aValue == null) return 1;
        if (bValue == null) return -1;

        // String comparison
        if (typeof aValue === 'string' && typeof bValue === 'string') {
          const result = aValue.localeCompare(bValue, undefined, {
            numeric: true,
            sensitivity: 'base',
          });
          if (result !== 0) {
            return config.direction === 'asc' ? result : -result;
          }
          continue;
        }

        // Number/Date comparison
        if (aValue < bValue) {
          return config.direction === 'asc' ? -1 : 1;
        }
        if (aValue > bValue) {
          return config.direction === 'asc' ? 1 : -1;
        }
      }

      return 0;
    });
  };

  return {
    sortConfigs,
    handleSort,
    sortData,
  };
};
