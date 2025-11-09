"use client";

import React, { useEffect, useRef, useState, useId } from 'react';

export interface TooltipProps {
  /** Tooltip content */
  content: React.ReactNode;
  /** Element to trigger tooltip */
  children: React.ReactElement;
  /** Tooltip placement */
  placement?: 'top' | 'bottom' | 'left' | 'right';
  /** Delay before showing (ms) */
  delay?: number;
  /** Show arrow */
  showArrow?: boolean;
  /** Disabled state */
  disabled?: boolean;
  /** Tooltip width */
  maxWidth?: string;
  /** Custom className for tooltip */
  className?: string;
}

export const Tooltip: React.FC<TooltipProps> = ({
  content,
  children,
  placement = 'top',
  delay = 200,
  showArrow = true,
  disabled = false,
  maxWidth = '300px',
  className = '',
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [tooltipPosition, setTooltipPosition] = useState({ top: 0, left: 0 });
  const triggerRef = useRef<HTMLDivElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);
  const timeoutRef = useRef<NodeJS.Timeout>();
  const tooltipId = useId();

  const calculatePosition = () => {
    if (!triggerRef.current || !tooltipRef.current) return;

    const triggerRect = triggerRef.current.getBoundingClientRect();
    const tooltipRect = tooltipRef.current.getBoundingClientRect();
    const scrollX = window.scrollX;
    const scrollY = window.scrollY;

    let top = 0;
    let left = 0;

    switch (placement) {
      case 'top':
        top = triggerRect.top + scrollY - tooltipRect.height - 8;
        left = triggerRect.left + scrollX + (triggerRect.width - tooltipRect.width) / 2;
        break;
      case 'bottom':
        top = triggerRect.bottom + scrollY + 8;
        left = triggerRect.left + scrollX + (triggerRect.width - tooltipRect.width) / 2;
        break;
      case 'left':
        top = triggerRect.top + scrollY + (triggerRect.height - tooltipRect.height) / 2;
        left = triggerRect.left + scrollX - tooltipRect.width - 8;
        break;
      case 'right':
        top = triggerRect.top + scrollY + (triggerRect.height - tooltipRect.height) / 2;
        left = triggerRect.right + scrollX + 8;
        break;
    }

    // Keep tooltip within viewport
    const padding = 8;
    if (left < scrollX + padding) {
      left = scrollX + padding;
    } else if (left + tooltipRect.width > scrollX + window.innerWidth - padding) {
      left = scrollX + window.innerWidth - tooltipRect.width - padding;
    }

    if (top < scrollY + padding) {
      top = scrollY + padding;
    } else if (top + tooltipRect.height > scrollY + window.innerHeight - padding) {
      top = scrollY + window.innerHeight - tooltipRect.height - padding;
    }

    setTooltipPosition({ top, left });
  };

  const showTooltip = () => {
    if (disabled) return;

    timeoutRef.current = setTimeout(() => {
      setIsVisible(true);
    }, delay);
  };

  const hideTooltip = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    setIsVisible(false);
  };

  useEffect(() => {
    if (isVisible) {
      calculatePosition();

      // Recalculate on window resize/scroll
      window.addEventListener('resize', calculatePosition);
      window.addEventListener('scroll', calculatePosition);

      return () => {
        window.removeEventListener('resize', calculatePosition);
        window.removeEventListener('scroll', calculatePosition);
      };
    }
  }, [isVisible]);

  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  const arrowClasses = {
    top: 'bottom-[-4px] left-1/2 -translate-x-1/2 border-l-transparent border-r-transparent border-b-transparent border-t-gray-900',
    bottom: 'top-[-4px] left-1/2 -translate-x-1/2 border-l-transparent border-r-transparent border-t-transparent border-b-gray-900',
    left: 'right-[-4px] top-1/2 -translate-y-1/2 border-t-transparent border-b-transparent border-r-transparent border-l-gray-900',
    right: 'left-[-4px] top-1/2 -translate-y-1/2 border-t-transparent border-b-transparent border-l-transparent border-r-gray-900',
  };

  // Helper to merge refs (supports both callback refs and RefObjects)
  const mergeRefs = (ref1: React.Ref<any>, ref2: React.Ref<any>) => {
    return (node: any) => {
      // Handle callback refs
      if (typeof ref1 === 'function') {
        ref1(node);
      } else if (ref1 && 'current' in ref1) {
        (ref1 as React.MutableRefObject<any>).current = node;
      }
      
      // Handle callback refs
      if (typeof ref2 === 'function') {
        ref2(node);
      } else if (ref2 && 'current' in ref2) {
        (ref2 as React.MutableRefObject<any>).current = node;
      }
    };
  };

  // Get existing ref from child if present
  const existingRef = (children as any).ref;
  const mergedRef = existingRef ? mergeRefs(existingRef, triggerRef) : triggerRef;

  const childWithProps = React.cloneElement(children, {
    ref: mergedRef,
    onMouseEnter: (e: React.MouseEvent) => {
      showTooltip();
      children.props.onMouseEnter?.(e);
    },
    onMouseLeave: (e: React.MouseEvent) => {
      hideTooltip();
      children.props.onMouseLeave?.(e);
    },
    onFocus: (e: React.FocusEvent) => {
      showTooltip();
      children.props.onFocus?.(e);
    },
    onBlur: (e: React.FocusEvent) => {
      hideTooltip();
      children.props.onBlur?.(e);
    },
    'aria-describedby': isVisible ? tooltipId : undefined,
  });

  return (
    <>
      {childWithProps}
      {isVisible && (
        <div
          ref={tooltipRef}
          id={tooltipId}
          role="tooltip"
          className={`
            fixed z-[9999] px-3 py-2 text-xs text-white bg-gray-900 rounded-md
            shadow-lg pointer-events-none
            animate-in fade-in-0 zoom-in-95 duration-200
            ${className}
          `}
          style={{
            top: `${tooltipPosition.top}px`,
            left: `${tooltipPosition.left}px`,
            maxWidth,
          }}
        >
          {content}
          {showArrow && (
            <div
              className={`absolute w-0 h-0 border-4 ${arrowClasses[placement]}`}
              aria-hidden="true"
            />
          )}
        </div>
      )}
    </>
  );
};

// Helper component for simple text tooltips
export interface SimpleTooltipProps extends Omit<TooltipProps, 'content'> {
  /** Tooltip text */
  text: string;
}

export const SimpleTooltip: React.FC<SimpleTooltipProps> = ({ text, ...props }) => {
  return <Tooltip content={<span>{text}</span>} {...props} />;
};
