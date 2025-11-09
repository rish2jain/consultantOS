"use client";

import React from "react";
import { X, Filter, Calendar } from "lucide-react";
import { Input } from "./Input";
import { Dropdown, DropdownItem } from "./Dropdown";
import { Button } from "./Button";

export interface FilterConfig {
  /** Column key */
  key: string;
  /** Filter type */
  type: "text" | "select" | "date" | "dateRange";
  /** Filter value */
  value: any;
  /** Select options (for type='select') */
  options?: Array<{ label: string; value: string }>;
}

export interface TableFiltersProps {
  /** Filter configurations */
  filters: FilterConfig[];
  /** Filter change handler */
  onFilterChange: (key: string, value: any) => void;
  /** Clear all filters handler */
  onClearAll: () => void;
  /** Show clear all button */
  showClearAll?: boolean;
  /** Compact mode */
  compact?: boolean;
  /** Custom className */
  className?: string;
}

export const TableFilters: React.FC<TableFiltersProps> = ({
  filters,
  onFilterChange,
  onClearAll,
  showClearAll = true,
  compact = false,
  className = "",
}) => {
  const hasActiveFilters = filters.some((filter) => {
    if (filter.type === "dateRange") {
      return filter.value?.from || filter.value?.to;
    }
    return filter.value !== "" && filter.value != null;
  });

  const containerClasses = ["flex items-center gap-3 flex-wrap", className]
    .filter(Boolean)
    .join(" ");

  return (
    <div className={containerClasses}>
      {filters.map((filter) => (
        <FilterInput
          key={filter.key}
          filter={filter}
          onChange={(value) => onFilterChange(filter.key, value)}
          compact={compact}
        />
      ))}

      {showClearAll && hasActiveFilters && (
        <Button
          variant="ghost"
          size={compact ? "sm" : "md"}
          onClick={onClearAll}
          leftIcon={<X className="w-4 h-4" />}
        >
          Clear all
        </Button>
      )}
    </div>
  );
};

interface FilterInputProps {
  filter: FilterConfig;
  onChange: (value: any) => void;
  compact?: boolean;
}

const FilterInput: React.FC<FilterInputProps> = ({
  filter,
  onChange,
  compact = false,
}) => {
  if (filter.type === "text") {
    return (
      <Input
        type="text"
        value={filter.value || ""}
        onChange={(e) => onChange(e.target.value)}
        placeholder={`Filter by ${filter.key}...`}
        size={compact ? "sm" : "md"}
        leftIcon={<Filter className="w-4 h-4" />}
        className="min-w-[200px]"
      />
    );
  }

  if (filter.type === "select") {
    const items: DropdownItem[] = [
      { label: "All", value: "" },
      ...(filter.options || []).map((opt) => ({
        label: opt.label,
        value: opt.value,
      })),
    ];

    return (
      <Dropdown
        trigger={
          <span className="flex items-center gap-2">
            <Filter className="w-4 h-4" />
            {items.find((item) => item.value === filter.value)?.label ||
              "Filter"}
          </span>
        }
        items={items}
        value={filter.value || ""}
        onChange={onChange}
        width="auto"
      />
    );
  }

  if (filter.type === "date") {
    return (
      <Input
        type="date"
        value={filter.value || ""}
        onChange={(e) => onChange(e.target.value)}
        size={compact ? "sm" : "md"}
        leftIcon={<Calendar className="w-4 h-4" />}
        className="min-w-[180px]"
      />
    );
  }

  if (filter.type === "dateRange") {
    const safeValue = filter.value || { from: '', to: '' };
    return (
      <div className="flex items-center gap-2">
        <Input
          type="date"
          value={safeValue.from || ""}
          onChange={(e) => onChange({ ...safeValue, from: e.target.value })}
          placeholder="From"
          size={compact ? "sm" : "md"}
          leftIcon={<Calendar className="w-4 h-4" />}
          className="min-w-[150px]"
        />
        <span className="text-gray-500">to</span>
        <Input
          type="date"
          value={safeValue.to || ""}
          onChange={(e) => onChange({ ...safeValue, to: e.target.value })}
          placeholder="To"
          size={compact ? "sm" : "md"}
          leftIcon={<Calendar className="w-4 h-4" />}
          className="min-w-[150px]"
        />
      </div>
    );
  }

  return null;
};

// Hook for managing table filters
export interface UseFiltersOptions<T> {
  /** Initial filter values */
  initialFilters?: Record<string, any>;
  /** Custom filter functions by column key */
  customFilters?: Record<string, (row: T, value: any) => boolean>;
}

export const useFilters = <T,>(options: UseFiltersOptions<T> = {}) => {
  const [filterValues, setFilterValues] = React.useState<Record<string, any>>(
    options.initialFilters || {}
  );

  const handleFilterChange = (key: string, value: any) => {
    setFilterValues((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  const handleClearAll = () => {
    setFilterValues({});
  };

  const filterData = (data: T[]): T[] => {
    return data.filter((row) => {
      return Object.entries(filterValues).every(([key, value]) => {
        // Skip empty filters
        if (value === "" || value == null) {
          return true;
        }

        // Handle date range
        if (typeof value === "object" && (value.from || value.to)) {
          const rowDate = new Date((row as any)[key]);
          if (isNaN(rowDate.getTime())) {
            return false; // Invalid date in row data
          }

          if (value.from) {
            const fromDate = new Date(value.from);
            if (!isNaN(fromDate.getTime()) && rowDate < fromDate) {
              return false;
            }
          }

          if (value.to) {
            const toDate = new Date(value.to);
            if (!isNaN(toDate.getTime()) && rowDate > toDate) {
              return false;
            }
          }

          return true;
        }

        // Use custom filter if provided
        if (options.customFilters?.[key]) {
          return options.customFilters[key](row, value);
        }

        // Default text/select filtering
        const rowValue = (row as any)[key];
        if (rowValue == null) return false;

        // Case-insensitive string matching
        const rowValueStr = String(rowValue).toLowerCase();
        const filterValueStr = String(value).toLowerCase();

        return rowValueStr.includes(filterValueStr);
      });
    });
  };

  const getActiveFilterCount = () => {
    return Object.values(filterValues).filter((value) => {
      if (typeof value === "object") {
        return value?.from || value?.to;
      }
      return value !== "" && value != null;
    }).length;
  };

  return {
    filterValues,
    handleFilterChange,
    handleClearAll,
    filterData,
    activeFilterCount: getActiveFilterCount(),
  };
};

// Column filter component for inline filtering
export interface ColumnFilterProps {
  /** Column key */
  columnKey: string;
  /** Column label */
  label: string;
  /** Filter type */
  type: "text" | "select" | "date" | "dateRange";
  /** Current filter value */
  value: any;
  /** Filter change handler */
  onChange: (value: any) => void;
  /** Select options (for type='select') */
  options?: Array<{ label: string; value: string }>;
  /** Compact mode */
  compact?: boolean;
}

export const ColumnFilter: React.FC<ColumnFilterProps> = ({
  columnKey,
  label,
  type,
  value,
  onChange,
  options,
  compact = false,
}) => {
  const [isOpen, setIsOpen] = React.useState(false);

  const hasFilter = React.useMemo(() => {
    if (type === "dateRange") {
      return value?.from || value?.to;
    }
    return value !== "" && value != null;
  }, [type, value]);

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className={`
          inline-flex items-center gap-1 px-2 py-1 text-xs rounded
          transition-colors
          ${
            hasFilter
              ? "bg-primary-100 text-primary-700 hover:bg-primary-200"
              : "text-gray-500 hover:bg-gray-100"
          }
        `}
        aria-label={`Filter ${label}`}
      >
        <Filter className="w-3 h-3" />
        {hasFilter && (
          <span className="w-1.5 h-1.5 bg-primary-600 rounded-full" />
        )}
      </button>

      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute top-full left-0 mt-1 z-20 bg-white border border-gray-200 rounded-md shadow-lg p-3 min-w-[200px]">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">
                Filter {label}
              </span>
              <button
                type="button"
                onClick={() => setIsOpen(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <FilterInput
              filter={{
                key: columnKey,
                type,
                value,
                options,
              }}
              onChange={onChange}
              compact={compact}
            />

            {hasFilter && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  onChange(type === "dateRange" ? { from: "", to: "" } : "");
                  setIsOpen(false);
                }}
                fullWidth
                className="mt-2"
              >
                Clear filter
              </Button>
            )}
          </div>
        </>
      )}
    </div>
  );
};
