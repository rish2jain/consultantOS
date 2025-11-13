"use client";

import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Minus, ArrowUp, ArrowDown } from 'lucide-react';
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

  // Respect user's reduced motion preference
  const prefersReducedMotion = typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  return (
    <motion.div
      whileHover={prefersReducedMotion ? {} : { y: -4 }}
      transition={prefersReducedMotion ? {} : { type: "spring", stiffness: 400, damping: 25 }}
      className="h-full"
    >
      <Card
        padding="md"
        hoverable={!!onClick}
        clickable={!!onClick}
        onClick={onClick}
        className="group h-full shadow-sm hover:shadow-md transition-shadow duration-200"
      >
        <div className="flex items-center justify-between">
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-600 truncate mb-1">
              {title}
            </p>
            <div className="flex items-baseline mt-2 gap-2">
              <motion.p
                initial={prefersReducedMotion ? false : { opacity: 0, scale: 0.9 }}
                animate={prefersReducedMotion ? {} : { opacity: 1, scale: 1 }}
                transition={prefersReducedMotion ? {} : { duration: 0.3 }}
                className="text-2xl font-bold text-gray-900"
              >
                {value}
              </motion.p>
              {trend && TrendIcon && (
                <motion.div
                  initial={prefersReducedMotion ? false : { opacity: 0, x: -10 }}
                  animate={prefersReducedMotion ? {} : { opacity: 1, x: 0 }}
                  transition={prefersReducedMotion ? {} : { delay: 0.1 }}
                  className={`flex items-center gap-1 ${trendColors[trend]}`}
                >
                  {trend === 'up' ? (
                    <ArrowUp className="w-3.5 h-3.5" />
                  ) : trend === 'down' ? (
                    <ArrowDown className="w-3.5 h-3.5" />
                  ) : (
                    <Minus className="w-3.5 h-3.5" />
                  )}
                  {trendValue && (
                    <span className="text-xs font-semibold">{trendValue}</span>
                  )}
                </motion.div>
              )}
            </div>
            {subtitle && (
              <p className="text-xs text-gray-500 mt-2 truncate">
                {subtitle}
              </p>
            )}
          </div>

          {icon && (
            <motion.div
              whileHover={prefersReducedMotion ? {} : { scale: 1.1, rotate: 3 }}
              transition={prefersReducedMotion ? {} : { type: "spring", stiffness: 400, damping: 25 }}
              className={`${colors.bg} text-white p-3 rounded-lg shadow-sm`}
            >
              {icon}
            </motion.div>
          )}
        </div>
      </Card>
    </motion.div>
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
