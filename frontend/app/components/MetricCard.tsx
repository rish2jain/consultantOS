"use client";

import React from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { Card } from './Card';

export interface MetricCardProps {
  /** Metric title */
  title: string;
  /** Main metric value */
  value: string | number;
  /** Icon element */
  icon?: React.ReactNode;
  /** Color variant */
  color?: 'blue' | 'green' | 'purple' | 'orange' | 'red' | 'gray';
  /** Trend direction */
  trend?: 'up' | 'down' | 'neutral';
  /** Trend percentage */
  trendValue?: string;
  /** Subtitle or description */
  subtitle?: string;
  /** Loading state */
  isLoading?: boolean;
  /** Click handler */
  onClick?: () => void;
}

const colorClasses = {
  blue: {
    bg: 'bg-blue-500',
    light: 'bg-blue-50',
    text: 'text-blue-600',
    ring: 'ring-blue-500',
  },
  green: {
    bg: 'bg-green-500',
    light: 'bg-green-50',
    text: 'text-green-600',
    ring: 'ring-green-500',
  },
  purple: {
    bg: 'bg-purple-500',
    light: 'bg-purple-50',
    text: 'text-purple-600',
    ring: 'ring-purple-500',
  },
  orange: {
    bg: 'bg-orange-500',
    light: 'bg-orange-50',
    text: 'text-orange-600',
    ring: 'ring-orange-500',
  },
  red: {
    bg: 'bg-red-500',
    light: 'bg-red-50',
    text: 'text-red-600',
    ring: 'ring-red-500',
  },
  gray: {
    bg: 'bg-gray-500',
    light: 'bg-gray-50',
    text: 'text-gray-600',
    ring: 'ring-gray-500',
  },
};

const trendIcons = {
  up: TrendingUp,
  down: TrendingDown,
  neutral: Minus,
};

const trendColors = {
  up: 'text-green-600',
  down: 'text-red-600',
  neutral: 'text-gray-400',
};

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  icon,
  color = 'blue',
  trend,
  trendValue,
  subtitle,
  isLoading = false,
  onClick,
}) => {
  const colors = colorClasses[color];
  const TrendIcon = trend ? trendIcons[trend] : null;

  if (isLoading) {
    return (
      <Card padding="md" className="animate-pulse">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <div className="h-4 bg-gray-200 rounded w-24 mb-2"></div>
            <div className="h-8 bg-gray-200 rounded w-32"></div>
          </div>
          <div className="w-12 h-12 bg-gray-200 rounded-lg"></div>
        </div>
      </Card>
    );
  }

  return (
    <Card
      padding="md"
      hoverable={!!onClick}
      clickable={!!onClick}
      onClick={onClick}
      className="group"
    >
      <div className="flex items-center justify-between">
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-gray-600 truncate">
            {title}
          </p>
          <div className="flex items-baseline mt-2 gap-2">
            <p className="text-2xl font-bold text-gray-900 transition-all duration-200 group-hover:scale-105">
              {value}
            </p>
            {trend && TrendIcon && (
              <div className={`flex items-center gap-1 ${trendColors[trend]}`}>
                <TrendIcon className="w-4 h-4" />
                {trendValue && (
                  <span className="text-sm font-medium">{trendValue}</span>
                )}
              </div>
            )}
          </div>
          {subtitle && (
            <p className="text-xs text-gray-500 mt-1 truncate">
              {subtitle}
            </p>
          )}
        </div>

        {icon && (
          <div
            className={`${colors.bg} text-white p-3 rounded-lg transition-all duration-200 group-hover:scale-110 group-hover:rotate-3`}
          >
            {icon}
          </div>
        )}
      </div>
    </Card>
  );
};

export const MetricCardSkeleton: React.FC = () => {
  return (
    <Card padding="md" className="animate-pulse">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <div className="h-4 bg-gray-200 rounded w-24 mb-2"></div>
          <div className="h-8 bg-gray-200 rounded w-32"></div>
        </div>
        <div className="w-12 h-12 bg-gray-200 rounded-lg"></div>
      </div>
    </Card>
  );
};
