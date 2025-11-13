"use client";

import React from 'react';
import { AlertCircle, CheckCircle, Eye, EyeOff } from 'lucide-react';

export interface InputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'size'> {
  /** Input label */
  label?: string;
  /** Helper text displayed below input */
  helperText?: string;
  /** Error message - sets error state */
  error?: string;
  /** Success state */
  success?: boolean;
  /** Input size */
  size?: 'sm' | 'md' | 'lg';
  /** Icon to display on the left */
  leftIcon?: React.ReactNode;
  /** Icon to display on the right */
  rightIcon?: React.ReactNode;
  /** Full width input */
  fullWidth?: boolean;
  /** Show character counter */
  showCounter?: boolean;
  /** Maximum length for counter */
  maxLength?: number;
}

const sizeClasses = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-base',
  lg: 'px-5 py-3 text-lg',
};

export const Input: React.FC<InputProps> = ({
  label,
  helperText,
  error,
  success,
  size = 'md',
  leftIcon,
  rightIcon,
  fullWidth = false,
  showCounter = false,
  maxLength,
  className = '',
  id,
  type = 'text',
  value,
  disabled,
  ...props
}) => {
  const [showPassword, setShowPassword] = React.useState(false);
  const generatedId = React.useId();
  const inputId = id || `input-${generatedId}`;

  const hasError = Boolean(error);
  const hasSuccess = success && !hasError;

  const baseClasses = 'w-full rounded-md border transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-1 disabled:opacity-50 disabled:cursor-not-allowed';

  const stateClasses = hasError
    ? 'border-red-300 focus:border-red-500 focus:ring-red-500'
    : hasSuccess
    ? 'border-green-300 focus:border-green-500 focus:ring-green-500'
    : 'border-gray-300 focus:border-primary-500 focus:ring-primary-500';

  const inputClasses = [
    baseClasses,
    stateClasses,
    sizeClasses[size],
    leftIcon ? 'pl-10' : '',
    rightIcon || type === 'password' ? 'pr-10' : '',
    className,
  ].filter(Boolean).join(' ');

  const handleValueChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (props.onChange) {
      props.onChange(e);
    }
  };

  const inputType = type === 'password' && showPassword ? 'text' : type;

  return (
    <div className={fullWidth ? 'w-full' : ''}>
      {label && (
        <label
          htmlFor={inputId}
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          {label}
          {props.required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}

      <div className="relative">
        {leftIcon && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none">
            {leftIcon}
          </div>
        )}

        <input
          id={inputId}
          type={inputType}
          value={value}
          disabled={disabled}
          maxLength={maxLength}
          className={inputClasses}
          aria-invalid={hasError}
          aria-required={props.required}
          aria-describedby={
            [
              hasError ? `${inputId}-error` : null,
              helperText ? `${inputId}-helper` : null,
              showCounter && maxLength ? `${inputId}-counter` : null,
            ].filter(Boolean).join(' ') || undefined
          }
          onChange={handleValueChange}
          {...props}
        />

        {type === 'password' && (
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
            aria-label={showPassword ? 'Hide password' : 'Show password'}
            tabIndex={-1}
          >
            {showPassword ? (
              <EyeOff className="w-5 h-5" />
            ) : (
              <Eye className="w-5 h-5" />
            )}
          </button>
        )}

        {/* Render icons with precedence: error > success > custom rightIcon (only when not password) */}
        {hasError && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2 text-red-500 pointer-events-none">
            <AlertCircle className="w-5 h-5" />
          </div>
        )}
        {!hasError && hasSuccess && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2 text-green-500 pointer-events-none">
            <CheckCircle className="w-5 h-5" />
          </div>
        )}
        {!hasError && !hasSuccess && rightIcon && type !== 'password' && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none">
            {rightIcon}
          </div>
        )}
      </div>

      <div className="mt-1 flex justify-between items-start">
        <div className="flex-1">
          {error && (
            <p
              id={`${inputId}-error`}
              className="text-sm text-red-600"
              role="alert"
            >
              {error}
            </p>
          )}
          {!error && helperText && (
            <p
              id={`${inputId}-helper`}
              className="text-sm text-gray-500"
            >
              {helperText}
            </p>
          )}
        </div>

        {showCounter && maxLength && (
          <span 
            id={`${inputId}-counter`}
            className="text-xs text-gray-400 ml-2 whitespace-nowrap"
            aria-live={value && maxLength && typeof value === 'string' && (value.length / maxLength) > 0.8 ? "polite" : "off"}
          >
            {typeof value === 'string' ? value.length : 0}/{maxLength}
          </span>
        )}
      </div>
    </div>
  );
};

// Convenience wrapper for password inputs
export const PasswordInput: React.FC<Omit<InputProps, 'type'>> = (props) => {
  return <Input type="password" {...props} />;
};
