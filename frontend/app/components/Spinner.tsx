"use client";

import React from 'react';
import { motion } from 'framer-motion';

export interface SpinnerProps {
  /** Spinner size */
  size?: 'sm' | 'md' | 'lg' | 'xl';
  /** Spinner color */
  color?: 'primary' | 'white' | 'gray' | 'inherit';
  /** Spinner variant */
  variant?: 'circular' | 'dots' | 'bars' | 'pulse';
  /** Custom className */
  className?: string;
  /** Accessibility label */
  label?: string;
}

const sizeClasses = {
  sm: 'w-4 h-4',
  md: 'w-6 h-6',
  lg: 'w-8 h-8',
  xl: 'w-12 h-12',
};

const colorClasses = {
  primary: 'border-primary-600',
  white: 'border-white',
  gray: 'border-gray-600',
  inherit: 'border-current',
};

const dotSizeClasses = {
  sm: 'w-1.5 h-1.5',
  md: 'w-2 h-2',
  lg: 'w-3 h-3',
  xl: 'w-4 h-4',
};

const barSizeClasses = {
  sm: 'w-1 h-3',
  md: 'w-1.5 h-4',
  lg: 'w-2 h-6',
  xl: 'w-3 h-8',
};

export const Spinner: React.FC<SpinnerProps> = ({
  size = 'md',
  color = 'primary',
  variant = 'circular',
  className = '',
  label = 'Loading...',
}) => {
  if (variant === 'circular') {
    return (
      <motion.div
        role="status"
        aria-label={label}
        className={`${sizeClasses[size]} ${className}`}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.2 }}
      >
        <motion.div
          className={`
            w-full h-full rounded-full border-2 border-gray-200
            ${colorClasses[color]} border-t-transparent
          `}
          animate={{ rotate: 360 }}
          transition={{
            duration: 1,
            repeat: Infinity,
            ease: "linear"
          }}
        />
        <span className="sr-only">{label}</span>
      </motion.div>
    );
  }

  if (variant === 'dots') {
    const dotColor = color === 'primary' ? 'bg-primary-600' :
                     color === 'white' ? 'bg-white' :
                     color === 'gray' ? 'bg-gray-600' : 'bg-current';

    return (
      <div
        role="status"
        aria-label={label}
        className={`flex items-center gap-1 ${className}`}
      >
        <div className={`${dotSizeClasses[size]} ${dotColor} rounded-full animate-bounce`} style={{ animationDelay: '0ms' }} />
        <div className={`${dotSizeClasses[size]} ${dotColor} rounded-full animate-bounce`} style={{ animationDelay: '150ms' }} />
        <div className={`${dotSizeClasses[size]} ${dotColor} rounded-full animate-bounce`} style={{ animationDelay: '300ms' }} />
        <span className="sr-only">{label}</span>
      </div>
    );
  }

  if (variant === 'bars') {
    const barColor = color === 'primary' ? 'bg-primary-600' :
                     color === 'white' ? 'bg-white' :
                     color === 'gray' ? 'bg-gray-600' : 'bg-current';

    return (
      <div
        role="status"
        aria-label={label}
        className={`flex items-center gap-1 ${className}`}
      >
        <div className={`${barSizeClasses[size]} ${barColor} rounded animate-pulse`} style={{ animationDelay: '0ms' }} />
        <div className={`${barSizeClasses[size]} ${barColor} rounded animate-pulse`} style={{ animationDelay: '150ms' }} />
        <div className={`${barSizeClasses[size]} ${barColor} rounded animate-pulse`} style={{ animationDelay: '300ms' }} />
        <span className="sr-only">{label}</span>
      </div>
    );
  }

  if (variant === 'pulse') {
    const pulseColor = color === 'primary' ? 'bg-primary-600' :
                       color === 'white' ? 'bg-white' :
                       color === 'gray' ? 'bg-gray-600' : 'bg-current';

    return (
      <div
        role="status"
        aria-label={label}
        className={`${className}`}
      >
        <div className={`${sizeClasses[size]} ${pulseColor} rounded-full animate-pulse`} />
        <span className="sr-only">{label}</span>
      </div>
    );
  }

  return null;
};

// Preset spinner components
export const PrimarySpinner: React.FC<Omit<SpinnerProps, 'color'>> = (props) => (
  <Spinner color="primary" {...props} />
);

export const WhiteSpinner: React.FC<Omit<SpinnerProps, 'color'>> = (props) => (
  <Spinner color="white" {...props} />
);

// Full page loading overlay
export interface LoadingOverlayProps {
  /** Whether overlay is visible */
  isLoading: boolean;
  /** Loading message */
  message?: string;
  /** Spinner size */
  size?: 'sm' | 'md' | 'lg' | 'xl';
  /** Background blur */
  blur?: boolean;
}

export const LoadingOverlay: React.FC<LoadingOverlayProps> = ({
  isLoading,
  message = 'Loading...',
  size = 'lg',
  blur = true,
}) => {
  if (!isLoading) return null;

  return (
    <div
      className={`
        fixed inset-0 z-50 flex flex-col items-center justify-center
        bg-black bg-opacity-50 transition-opacity duration-200
        ${blur ? 'backdrop-blur-sm' : ''}
      `}
    >
      <Spinner size={size} color="white" />
      {message && (
        <p className="mt-4 text-white text-sm font-medium">
          {message}
        </p>
      )}
    </div>
  );
};

// Inline loading state
export interface InlineLoadingProps {
  /** Loading message */
  message?: string;
  /** Spinner size */
  size?: 'sm' | 'md' | 'lg' | 'xl';
  /** Center content */
  centered?: boolean;
  /** Custom className */
  className?: string;
}

export const InlineLoading: React.FC<InlineLoadingProps> = ({
  message = 'Loading...',
  size = 'md',
  centered = false,
  className = '',
}) => {
  return (
    <div
      className={`
        flex items-center gap-3
        ${centered ? 'justify-center' : ''}
        ${className}
      `}
    >
      <Spinner size={size} />
      {message && (
        <span className="text-sm text-gray-600">
          {message}
        </span>
      )}
    </div>
  );
};
