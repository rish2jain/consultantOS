"use client";

import React, { useEffect, useState, useCallback } from 'react';
import { X, Info, CheckCircle, AlertTriangle, XCircle } from 'lucide-react';

export interface AlertProps {
  /** Alert variant */
  variant?: 'info' | 'success' | 'warning' | 'error';
  /** Alert title */
  title?: string;
  /** Alert description */
  description?: string | React.ReactNode;
  /** Show close button */
  dismissible?: boolean;
  /** Close handler */
  onClose?: () => void;
  /** Auto dismiss after timeout (ms) */
  autoDismiss?: number;
  /** Show icon */
  showIcon?: boolean;
  /** Action buttons */
  actions?: React.ReactNode;
  /** Children (alternative to description) */
  children?: React.ReactNode;
  /** Custom className */
  className?: string;
}

const variantConfig = {
  info: {
    container: 'bg-blue-50 border-blue-200',
    icon: 'text-blue-600',
    title: 'text-blue-900',
    description: 'text-blue-700',
    IconComponent: Info,
  },
  success: {
    container: 'bg-green-50 border-green-200',
    icon: 'text-green-600',
    title: 'text-green-900',
    description: 'text-green-700',
    IconComponent: CheckCircle,
  },
  warning: {
    container: 'bg-yellow-50 border-yellow-200',
    icon: 'text-yellow-600',
    title: 'text-yellow-900',
    description: 'text-yellow-700',
    IconComponent: AlertTriangle,
  },
  error: {
    container: 'bg-red-50 border-red-200',
    icon: 'text-red-600',
    title: 'text-red-900',
    description: 'text-red-700',
    IconComponent: XCircle,
  },
};

export const Alert: React.FC<AlertProps> = ({
  variant = 'info',
  title,
  description,
  dismissible = false,
  onClose,
  autoDismiss,
  showIcon = true,
  actions,
  children,
  className = '',
}) => {
  const [isVisible, setIsVisible] = useState(true);
  const config = variantConfig[variant];
  const IconComponent = config.IconComponent;

  const handleClose = useCallback(() => {
    setIsVisible(false);
    onClose?.();
  }, [onClose]);

  useEffect(() => {
    if (autoDismiss && autoDismiss > 0) {
      const timer = setTimeout(() => {
        handleClose();
      }, autoDismiss);

      return () => clearTimeout(timer);
    }
  }, [autoDismiss, handleClose]);

  if (!isVisible) return null;

  return (
    <div
      role="alert"
      className={`
        relative flex gap-3 p-4 border rounded-lg
        ${config.container}
        ${className}
      `}
    >
      {showIcon && (
        <div className="flex-shrink-0">
          <IconComponent className={`w-5 h-5 ${config.icon}`} aria-hidden="true" />
        </div>
      )}

      <div className="flex-1 min-w-0">
        {title && (
          <h3 className={`text-sm font-semibold ${config.title}`}>
            {title}
          </h3>
        )}

        {(description || children) && (
          <div className={`text-sm mt-1 ${config.description} ${title ? 'mt-1' : ''}`}>
            {children || description}
          </div>
        )}

        {actions && (
          <div className="flex gap-2 mt-3">
            {actions}
          </div>
        )}
      </div>

      {dismissible && (
        <button
          type="button"
          onClick={handleClose}
          className={`
            flex-shrink-0 inline-flex rounded-md p-1.5
            hover:bg-black hover:bg-opacity-10
            focus:outline-none focus:ring-2 focus:ring-offset-2
            ${config.icon}
            transition-colors
          `}
          aria-label="Dismiss alert"
        >
          <X className="w-4 h-4" aria-hidden="true" />
        </button>
      )}
    </div>
  );
};

// Preset alert components for common use cases
export const InfoAlert: React.FC<Omit<AlertProps, 'variant'>> = (props) => (
  <Alert variant="info" {...props} />
);

export const SuccessAlert: React.FC<Omit<AlertProps, 'variant'>> = (props) => (
  <Alert variant="success" {...props} />
);

export const WarningAlert: React.FC<Omit<AlertProps, 'variant'>> = (props) => (
  <Alert variant="warning" {...props} />
);

export const ErrorAlert: React.FC<Omit<AlertProps, 'variant'>> = (props) => (
  <Alert variant="error" {...props} />
);

// Custom hook for managing alert state
export const useAlert = () => {
  const [alerts, setAlerts] = useState<Array<{
    id: string;
    variant: 'info' | 'success' | 'warning' | 'error';
    title?: string;
    description?: string;
  }>>([]);

  const showAlert = (
    variant: 'info' | 'success' | 'warning' | 'error',
    title?: string,
    description?: string,
  ) => {
    const id = Math.random().toString(36).substring(7);
    setAlerts(prev => [...prev, { id, variant, title, description }]);
    return id;
  };

  const hideAlert = (id: string) => {
    setAlerts(prev => prev.filter(alert => alert.id !== id));
  };

  const clearAlerts = () => {
    setAlerts([]);
  };

  return {
    alerts,
    showAlert,
    hideAlert,
    clearAlerts,
    info: (title?: string, description?: string) => showAlert('info', title, description),
    success: (title?: string, description?: string) => showAlert('success', title, description),
    warning: (title?: string, description?: string) => showAlert('warning', title, description),
    error: (title?: string, description?: string) => showAlert('error', title, description),
  };
};
