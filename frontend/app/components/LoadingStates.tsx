'use client';

import React from 'react';
import { motion } from 'framer-motion';

/**
 * Loading Skeleton Components for Strategic Intelligence Visualizations
 */

// Base skeleton component
export const Skeleton: React.FC<{
  height?: string;
  width?: string;
  className?: string;
  rounded?: 'sm' | 'md' | 'lg' | 'full';
}> = ({ height = 'h-4', width = 'w-full', className = '', rounded = 'md' }) => {
  const roundedClasses = {
    sm: 'rounded-sm',
    md: 'rounded-md',
    lg: 'rounded-lg',
    full: 'rounded-full',
  };

  return (
    <div
      className={`${height} ${width} bg-gray-200 ${roundedClasses[rounded]} animate-pulse ${className}`}
    />
  );
};

// System Dynamics Map Loading
export const SystemDynamicsMapLoading: React.FC = () => (
  <div className="bg-white rounded-lg shadow-lg p-6">
    <div className="flex justify-between items-center mb-4">
      <Skeleton height="h-8" width="w-64" />
      <div className="flex gap-2">
        <Skeleton height="h-10" width="w-32" />
        <Skeleton height="h-10" width="w-32" />
      </div>
    </div>

    <div className="flex gap-4">
      {/* Main visualization area */}
      <div className="flex-1">
        <div className="border border-gray-200 rounded-lg p-8 flex items-center justify-center" style={{ height: '600px' }}>
          <div className="text-center">
            <motion.div
              animate={{
                scale: [1, 1.1, 1],
                rotate: [0, 360],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: 'linear',
              }}
              className="mx-auto mb-4"
            >
              <svg className="w-16 h-16 text-blue-600" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
            </motion.div>
            <p className="text-sm text-gray-600">Building system dynamics map...</p>
          </div>
        </div>
      </div>

      {/* Side panel */}
      <div className="w-80 space-y-4">
        <div className="bg-gray-50 rounded-lg p-4">
          <Skeleton height="h-5" width="w-24" className="mb-3" />
          <div className="space-y-2">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="flex items-center gap-2">
                <Skeleton height="h-4" width="w-4" rounded="full" />
                <Skeleton height="h-3" width="w-32" />
              </div>
            ))}
          </div>
        </div>

        <div className="bg-gray-50 rounded-lg p-4">
          <Skeleton height="h-5" width="w-32" className="mb-3" />
          <div className="space-y-2">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} height="h-16" width="w-full" />
            ))}
          </div>
        </div>
      </div>
    </div>
  </div>
);

// Flywheel Dashboard Loading
export const FlywheelDashboardLoading: React.FC = () => (
  <div className="bg-white rounded-lg shadow-lg p-6">
    <div className="flex items-center justify-between mb-6">
      <Skeleton height="h-8" width="w-64" />
      <Skeleton height="h-10" width="w-32" />
    </div>

    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
      {/* Central Gauge */}
      <div className="lg:col-span-1">
        <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg p-6">
          <Skeleton height="h-6" width="w-48" className="mb-4 mx-auto" />
          <div className="flex items-center justify-center">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
              className="w-64 h-64 border-8 border-gray-300 border-t-blue-600 rounded-full"
            />
          </div>
        </div>
      </div>

      {/* Component Breakdown */}
      <div className="lg:col-span-2">
        <Skeleton height="h-6" width="w-48" className="mb-4" />
        <div className="grid grid-cols-1 gap-4">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Skeleton height="h-16" width="w-16" rounded="full" />
                  <div>
                    <Skeleton height="h-4" width="w-32" className="mb-2" />
                    <Skeleton height="h-3" width="w-24" />
                  </div>
                </div>
                <Skeleton height="h-12" width="w-40" />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  </div>
);

// Intelligence Feed Loading
export const IntelligenceFeedLoading: React.FC = () => (
  <div className="bg-white rounded-lg shadow-lg">
    <div className="border-b border-gray-200 p-4">
      <div className="flex items-center justify-between mb-4">
        <Skeleton height="h-8" width="w-48" />
        <div className="flex gap-2">
          <Skeleton height="h-10" width="w-24" />
          <Skeleton height="h-10" width="w-32" />
        </div>
      </div>
      <div className="flex flex-wrap gap-2">
        {[1, 2, 3, 4, 5].map((i) => (
          <Skeleton key={i} height="h-7" width="w-24" rounded="full" />
        ))}
      </div>
    </div>

    <div className="p-4 space-y-3">
      {[1, 2, 3, 4, 5].map((i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.1 }}
          className="border border-gray-200 rounded-lg p-4"
        >
          <div className="flex items-start justify-between mb-2">
            <div className="flex items-center gap-2 flex-1">
              <Skeleton height="h-6" width="w-6" rounded="full" />
              <Skeleton height="h-4" width="w-48" />
            </div>
            <Skeleton height="h-3" width="w-16" />
          </div>
          <Skeleton height="h-3" width="w-full" className="mb-1" />
          <Skeleton height="h-3" width="w-3/4" className="mb-3" />
          <div className="flex gap-2">
            <Skeleton height="h-6" width="w-20" rounded="full" />
            <Skeleton height="h-6" width="w-24" rounded="full" />
          </div>
        </motion.div>
      ))}
    </div>
  </div>
);

// Executive Brief Loading
export const ExecutiveBriefLoading: React.FC = () => (
  <div className="space-y-6">
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between">
        <div>
          <Skeleton height="h-6" width="w-48" className="mb-4" />
          <Skeleton height="h-16" width="w-32" />
        </div>
        <Skeleton height="h-4" width="w-40" />
      </div>
    </div>

    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {[1, 2].map((i) => (
        <div key={i} className="bg-white rounded-lg shadow-lg p-6">
          <Skeleton height="h-6" width="w-32" className="mb-4" />
          <div className="space-y-3">
            {[1, 2, 3].map((j) => (
              <div key={j} className="bg-gray-50 rounded-lg p-4">
                <Skeleton height="h-5" width="w-64" className="mb-2" />
                <Skeleton height="h-3" width="w-48" className="mb-3" />
                <Skeleton height="h-3" width="w-full" />
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  </div>
);

// Full Dashboard Loading
export const DashboardLoading: React.FC = () => (
  <div className="min-h-screen bg-gray-50">
    <div className="bg-white border-b border-gray-200 p-6">
      <div className="max-w-7xl mx-auto">
        <Skeleton height="h-10" width="w-64" className="mb-4" />
        <div className="flex gap-2">
          <Skeleton height="h-12" width="w-40" />
          <Skeleton height="h-12" width="w-40" />
          <Skeleton height="h-12" width="w-40" />
        </div>
      </div>
    </div>

    <div className="max-w-7xl mx-auto px-6 py-6">
      <ExecutiveBriefLoading />
    </div>
  </div>
);

// Spinner Component
export const Spinner: React.FC<{ size?: 'sm' | 'md' | 'lg'; className?: string }> = ({
  size = 'md',
  className = '',
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  };

  return (
    <motion.div
      animate={{ rotate: 360 }}
      transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
      className={`${sizeClasses[size]} ${className}`}
    >
      <svg className="w-full h-full" fill="none" viewBox="0 0 24 24">
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        />
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
    </motion.div>
  );
};

// Empty State Component
export const EmptyState: React.FC<{
  icon?: string;
  title: string;
  description?: string;
  action?: {
    label: string;
    onClick: () => void;
  };
}> = ({ icon = '📊', title, description, action }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    className="flex flex-col items-center justify-center py-16 px-6"
  >
    <div className="text-6xl mb-4">{icon}</div>
    <h3 className="text-xl font-semibold text-gray-900 mb-2">{title}</h3>
    {description && (
      <p className="text-sm text-gray-600 text-center mb-6 max-w-md">{description}</p>
    )}
    {action && (
      <button
        onClick={action.onClick}
        className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
      >
        {action.label}
      </button>
    )}
  </motion.div>
);

// Progress Bar Component
export const ProgressBar: React.FC<{
  progress: number; // 0-100
  label?: string;
  showPercentage?: boolean;
  color?: 'blue' | 'green' | 'yellow' | 'red';
}> = ({ progress, label, showPercentage = true, color = 'blue' }) => {
  const colorClasses = {
    blue: 'bg-blue-600',
    green: 'bg-green-600',
    yellow: 'bg-yellow-600',
    red: 'bg-red-600',
  };

  return (
    <div className="w-full">
      {(label || showPercentage) && (
        <div className="flex justify-between items-center mb-2">
          {label && <span className="text-sm text-gray-700">{label}</span>}
          {showPercentage && (
            <span className="text-sm font-medium text-gray-900">{progress}%</span>
          )}
        </div>
      )}
      <div className="w-full bg-gray-200 rounded-full h-2">
        <motion.div
          className={`${colorClasses[color]} h-2 rounded-full`}
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
        />
      </div>
    </div>
  );
};

export default {
  Skeleton,
  SystemDynamicsMapLoading,
  FlywheelDashboardLoading,
  IntelligenceFeedLoading,
  ExecutiveBriefLoading,
  DashboardLoading,
  Spinner,
  EmptyState,
  ProgressBar,
};
