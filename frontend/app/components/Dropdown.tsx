"use client";

import React, { useEffect, useRef, useState } from 'react';
import { ChevronDown } from 'lucide-react';

export interface DropdownItem {
  label: string;
  value: string;
  icon?: React.ReactNode;
  disabled?: boolean;
  onClick?: () => void;
}

export interface DropdownProps {
  /** Trigger button content */
  trigger?: React.ReactNode;
  /** Dropdown items */
  items: DropdownItem[];
  /** Selected value (for controlled mode) */
  value?: string;
  /** Change handler */
  onChange?: (value: string) => void;
  /** Dropdown placement */
  placement?: 'bottom-start' | 'bottom-end' | 'top-start' | 'top-end';
  /** Dropdown width */
  width?: 'auto' | 'full' | 'trigger';
  /** Disabled state */
  disabled?: boolean;
  /** Custom trigger button class */
  triggerClassName?: string;
}

export const Dropdown: React.FC<DropdownProps> = ({
  trigger,
  items,
  value,
  onChange,
  placement = 'bottom-start',
  width = 'trigger',
  disabled = false,
  triggerClassName = '',
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLButtonElement | HTMLDivElement>(null);

  // Close on click outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  // Close on Escape key
  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setIsOpen(false);
        triggerRef.current?.focus();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen]);

  // Keyboard navigation
  const handleKeyDown = (event: React.KeyboardEvent, index: number) => {
    if (event.key === 'ArrowDown') {
      event.preventDefault();
      // Find next enabled item, wrapping around
      let nextIndex = (index + 1) % items.length;
      let attempts = 0;
      while (items[nextIndex].disabled && attempts < items.length) {
        nextIndex = (nextIndex + 1) % items.length;
        attempts++;
      }
      if (!items[nextIndex].disabled) {
        const nextItem = dropdownRef.current?.querySelectorAll('[role="menuitem"]')[nextIndex] as HTMLElement;
        nextItem?.focus();
      }
    } else if (event.key === 'ArrowUp') {
      event.preventDefault();
      // Find previous enabled item, wrapping around
      let prevIndex = index === 0 ? items.length - 1 : index - 1;
      let attempts = 0;
      while (items[prevIndex].disabled && attempts < items.length) {
        prevIndex = prevIndex === 0 ? items.length - 1 : prevIndex - 1;
        attempts++;
      }
      if (!items[prevIndex].disabled) {
        const prevItem = dropdownRef.current?.querySelectorAll('[role="menuitem"]')[prevIndex] as HTMLElement;
        prevItem?.focus();
      }
    } else if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      if (!items[index].disabled) {
        handleItemClick(items[index]);
      }
    }
  };

  const handleItemClick = (item: DropdownItem) => {
    if (item.disabled) return;

    onChange?.(item.value);
    item.onClick?.();
    setIsOpen(false);
    triggerRef.current?.focus();
  };

  const placementClasses = {
    'bottom-start': 'top-full left-0 mt-2',
    'bottom-end': 'top-full right-0 mt-2',
    'top-start': 'bottom-full left-0 mb-2',
    'top-end': 'bottom-full right-0 mb-2',
  };

  const widthClasses = {
    auto: 'w-auto',
    full: 'w-full',
    trigger: 'w-auto', // Match trigger's intrinsic width
  };

  const defaultTrigger = (
    <span className="flex items-center gap-2">
      {items.find(item => item.value === value)?.label || 'Select...'}
      <ChevronDown className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
    </span>
  );

  const handleTriggerClick = (e: React.MouseEvent) => {
    if (!disabled) {
      setIsOpen(!isOpen);
    }
    // If trigger is a custom element, allow it to handle its own click
    if (trigger) {
      e.stopPropagation();
    }
  };

  return (
    <div className="relative inline-block" ref={dropdownRef}>
      {trigger ? (
        <div
          ref={triggerRef as React.RefObject<HTMLDivElement>}
          onClick={handleTriggerClick}
          className={triggerClassName}
          role="button"
          tabIndex={disabled ? -1 : 0}
          aria-haspopup="true"
          aria-expanded={isOpen}
          aria-disabled={disabled}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              if (!disabled) {
                setIsOpen(!isOpen);
              }
            }
          }}
        >
          {trigger}
        </div>
      ) : (
        <button
          ref={triggerRef}
          type="button"
          onClick={handleTriggerClick}
          disabled={disabled}
          className={`
            inline-flex items-center justify-between px-4 py-2
            text-sm font-medium text-gray-700 bg-white border border-gray-300
            rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2
            focus:ring-primary-500 focus:ring-offset-2 transition-colors
            disabled:opacity-50 disabled:cursor-not-allowed
            ${triggerClassName}
          `}
          aria-haspopup="true"
          aria-expanded={isOpen}
        >
          {defaultTrigger}
        </button>
      )}

      {isOpen && (
        <div
          className={`
            absolute z-50 ${placementClasses[placement]} ${widthClasses[width]}
            min-w-[12rem] bg-white border border-gray-200 rounded-md shadow-lg
            py-1 max-h-60 overflow-auto
          `}
          role="menu"
          aria-orientation="vertical"
        >
          {items.map((item, index) => (
            <button
              key={item.value}
              type="button"
              role="menuitem"
              tabIndex={0}
              onClick={() => handleItemClick(item)}
              onKeyDown={(e) => handleKeyDown(e, index)}
              disabled={item.disabled}
              className={`
                w-full flex items-center gap-2 px-4 py-2 text-sm text-left
                transition-colors
                ${item.value === value ? 'bg-primary-50 text-primary-700' : 'text-gray-700'}
                ${item.disabled
                  ? 'opacity-50 cursor-not-allowed'
                  : 'hover:bg-gray-100 cursor-pointer'
                }
                focus:outline-none focus:bg-gray-100
              `}
            >
              {item.icon && <span className="flex-shrink-0">{item.icon}</span>}
              <span className="flex-1">{item.label}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

export const useDropdown = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedValue, setSelectedValue] = useState<string>('');

  const open = () => setIsOpen(true);
  const close = () => setIsOpen(false);
  const toggle = () => setIsOpen(!isOpen);
  const select = (value: string) => setSelectedValue(value);

  return { isOpen, open, close, toggle, selectedValue, select };
};
