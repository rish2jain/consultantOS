"use client";

import React from 'react';
import { motion } from 'framer-motion';
import { X } from 'lucide-react';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  /** Badge variant */
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'danger' | 'info';
  /** Badge size */
  size?: 'sm' | 'md' | 'lg';
  /** Removable badge with X button */
  removable?: boolean;
  /** Remove handler */
  onRemove?: () => void;
  /** Dot indicator */
  dot?: boolean;
  /** Children */
  children: React.ReactNode;
}

const variantClasses = {
  default: 'bg-gray-100 text-gray-800',
  primary: 'bg-primary-100 text-primary-800',
  success: 'bg-green-100 text-green-800',
  warning: 'bg-yellow-100 text-yellow-800',
  danger: 'bg-red-100 text-red-800',
  info: 'bg-blue-100 text-blue-800',
};

const sizeClasses = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-2.5 py-0.5 text-sm',
  lg: 'px-3 py-1 text-base',
};

const dotColors = {
  default: 'bg-gray-400',
  primary: 'bg-primary-500',
  success: 'bg-green-500',
  warning: 'bg-yellow-500',
  danger: 'bg-red-500',
  info: 'bg-blue-500',
};

export const Badge: React.FC<BadgeProps> = ({
  variant = 'default',
  size = 'md',
  removable = false,
  onRemove,
  dot = false,
  className = '',
  children,
  ...props
}) => {
  const baseClasses = 'inline-flex items-center gap-1.5 rounded-full font-medium transition-colors';

  const classes = [
    baseClasses,
    variantClasses[variant],
    sizeClasses[size],
    className,
  ].filter(Boolean).join(' ');

  return (
    <motion.span
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ scale: 1.05 }}
      className={classes}
      {...props}
    >
      {dot && (
        <motion.span
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          className={`w-2 h-2 rounded-full ${dotColors[variant]}`}
          aria-hidden="true"
        />
      )}
      {children}
      {removable && onRemove && (
        <motion.button
          type="button"
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={(e) => {
            e.stopPropagation();
            onRemove();
          }}
          className="hover:bg-black hover:bg-opacity-10 rounded-full p-0.5 transition-colors"
          aria-label="Remove"
        >
          <X className="w-3 h-3" />
        </motion.button>
      )}
    </motion.span>
  );
};
