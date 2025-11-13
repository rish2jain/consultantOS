"use client";

import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './Card';
import { Button } from './Button';
import { Badge } from './Badge';
import { X, Filter } from 'lucide-react';
import type { Template } from '@/types/templates';

export interface TemplateFiltersState {
  categories: Template['category'][];
  frameworks: Template['framework_type'][];
  visibility: Template['visibility'] | null;
  industry: string;
  region: string;
}

export interface TemplateFiltersProps {
  /** Current filter state */
  filters: TemplateFiltersState;
  /** Filter change handler */
  onChange: (filters: TemplateFiltersState) => void;
  /** Show filters (for mobile toggle) */
  show?: boolean;
}

const categoryOptions: { value: Template['category']; label: string }[] = [
  { value: 'strategic', label: 'Strategic' },
  { value: 'financial', label: 'Financial' },
  { value: 'operational', label: 'Operational' },
  { value: 'market', label: 'Market' },
  { value: 'risk', label: 'Risk' },
];

const frameworkOptions: { value: Template['framework_type']; label: string }[] = [
  { value: 'porter', label: "Porter's 5 Forces" },
  { value: 'swot', label: 'SWOT' },
  { value: 'pestel', label: 'PESTEL' },
  { value: 'blue_ocean', label: 'Blue Ocean' },
];

const visibilityOptions: { value: Template['visibility']; label: string }[] = [
  { value: 'public', label: 'Public' },
  { value: 'private', label: 'Private' },
  { value: 'shared', label: 'Shared' },
];

export const TemplateFilters: React.FC<TemplateFiltersProps> = ({
  filters,
  onChange,
  show = true,
}) => {
  const toggleCategory = (category: Template['category']) => {
    const newCategories = filters.categories.includes(category)
      ? filters.categories.filter(c => c !== category)
      : [...filters.categories, category];
    onChange({ ...filters, categories: newCategories });
  };

  const toggleFramework = (framework: Template['framework_type']) => {
    const newFrameworks = filters.frameworks.includes(framework)
      ? filters.frameworks.filter(f => f !== framework)
      : [...filters.frameworks, framework];
    onChange({ ...filters, frameworks: newFrameworks });
  };

  const setVisibility = (visibility: Template['visibility'] | null) => {
    onChange({ ...filters, visibility });
  };

  const clearFilters = () => {
    onChange({
      categories: [],
      frameworks: [],
      visibility: null,
      industry: '',
      region: '',
    });
  };

  const hasActiveFilters =
    filters.categories.length > 0 ||
    filters.frameworks.length > 0 ||
    filters.visibility !== null ||
    filters.industry !== '' ||
    filters.region !== '';

  if (!show) return null;

  return (
    <Card variant="outlined" padding="md" className="sticky top-4">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-gray-600" aria-hidden="true" />
            <CardTitle>Filters</CardTitle>
          </div>
          {hasActiveFilters && (
            <Button
              variant="ghost"
              size="sm"
              onClick={clearFilters}
              leftIcon={<X className="w-4 h-4" />}
            >
              Clear
            </Button>
          )}
        </div>
      </CardHeader>

      <CardContent>
        <div className="space-y-6">
          {/* Category Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Category
            </label>
            <div className="space-y-2">
              {categoryOptions.map((option) => (
                <label
                  key={option.value}
                  className="flex items-center gap-2 cursor-pointer group"
                >
                  <input
                    type="checkbox"
                    checked={filters.categories.includes(option.value)}
                    onChange={() => toggleCategory(option.value)}
                    className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500 focus:ring-2 cursor-pointer"
                  />
                  <span className="text-sm text-gray-700 group-hover:text-gray-900">
                    {option.label}
                  </span>
                  {filters.categories.includes(option.value) && (
                    <Badge variant="primary" size="sm">
                      Active
                    </Badge>
                  )}
                </label>
              ))}
            </div>
          </div>

          {/* Framework Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Framework Type
            </label>
            <div className="space-y-2">
              {frameworkOptions.map((option) => (
                <label
                  key={option.value}
                  className="flex items-center gap-2 cursor-pointer group"
                >
                  <input
                    type="checkbox"
                    checked={filters.frameworks.includes(option.value)}
                    onChange={() => toggleFramework(option.value)}
                    className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500 focus:ring-2 cursor-pointer"
                  />
                  <span className="text-sm text-gray-700 group-hover:text-gray-900">
                    {option.label}
                  </span>
                  {filters.frameworks.includes(option.value) && (
                    <Badge variant="primary" size="sm">
                      Active
                    </Badge>
                  )}
                </label>
              ))}
            </div>
          </div>

          {/* Visibility Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Visibility
            </label>
            <div className="space-y-2">
              <label className="flex items-center gap-2 cursor-pointer group">
                <input
                  type="radio"
                  name="visibility"
                  checked={filters.visibility === null}
                  onChange={() => setVisibility(null)}
                  className="w-4 h-4 text-primary-600 border-gray-300 focus:ring-primary-500 focus:ring-2 cursor-pointer"
                />
                <span className="text-sm text-gray-700 group-hover:text-gray-900">
                  All
                </span>
              </label>
              {visibilityOptions.map((option) => (
                <label
                  key={option.value}
                  className="flex items-center gap-2 cursor-pointer group"
                >
                  <input
                    type="radio"
                    name="visibility"
                    checked={filters.visibility === option.value}
                    onChange={() => setVisibility(option.value)}
                    className="w-4 h-4 text-primary-600 border-gray-300 focus:ring-primary-500 focus:ring-2 cursor-pointer"
                  />
                  <span className="text-sm text-gray-700 group-hover:text-gray-900">
                    {option.label}
                  </span>
                </label>
              ))}
            </div>
          </div>

          {/* Industry Filter */}
          <div>
            <label
              htmlFor="industry-filter"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Industry
            </label>
            <input
              id="industry-filter"
              type="text"
              value={filters.industry}
              onChange={(e) => onChange({ ...filters, industry: e.target.value })}
              placeholder="e.g., Technology, Healthcare"
              className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>

          {/* Region Filter */}
          <div>
            <label
              htmlFor="region-filter"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Region
            </label>
            <input
              id="region-filter"
              type="text"
              value={filters.region}
              onChange={(e) => onChange({ ...filters, region: e.target.value })}
              placeholder="e.g., North America, APAC"
              className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
export default TemplateFilters;
