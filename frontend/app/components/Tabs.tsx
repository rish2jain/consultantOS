"use client";

import React, { createContext, useContext, useState } from 'react';

interface TabsContextValue {
  activeTab: string;
  setActiveTab: (value: string) => void;
  orientation: 'horizontal' | 'vertical';
}

const TabsContext = createContext<TabsContextValue | undefined>(undefined);

const useTabsContext = () => {
  const context = useContext(TabsContext);
  if (!context) {
    throw new Error('Tabs components must be used within a Tabs component');
  }
  return context;
};

export interface TabsProps {
  /** Default active tab */
  defaultValue?: string;
  /** Controlled active tab */
  value?: string;
  /** Change handler */
  onValueChange?: (value: string) => void;
  /** Tab orientation */
  orientation?: 'horizontal' | 'vertical';
  /** Children */
  children: React.ReactNode;
  /** Custom className */
  className?: string;
}

export const Tabs: React.FC<TabsProps> = ({
  defaultValue,
  value,
  onValueChange,
  orientation = 'horizontal',
  children,
  className = '',
}) => {
  const [activeTab, setActiveTab] = useState(defaultValue || '');

  const handleTabChange = (newValue: string) => {
    if (value === undefined) {
      setActiveTab(newValue);
    }
    onValueChange?.(newValue);
  };

  const currentTab = value !== undefined ? value : activeTab;

  return (
    <TabsContext.Provider
      value={{
        activeTab: currentTab,
        setActiveTab: handleTabChange,
        orientation,
      }}
    >
      <div
        className={`${orientation === 'vertical' ? 'flex gap-4' : ''} ${className}`}
      >
        {children}
      </div>
    </TabsContext.Provider>
  );
};

export interface TabListProps {
  /** Children */
  children: React.ReactNode;
  /** Custom className */
  className?: string;
}

export const TabList: React.FC<TabListProps> = ({ children, className = '' }) => {
  const { orientation } = useTabsContext();

  const handleKeyDown = (event: React.KeyboardEvent) => {
    const tabList = event.currentTarget;
    const tabs = Array.from(tabList.querySelectorAll('[role="tab"]')) as HTMLElement[];
    const currentIndex = tabs.findIndex(tab => tab === document.activeElement);

    let nextIndex = currentIndex;

    if (orientation === 'horizontal') {
      if (event.key === 'ArrowLeft') {
        event.preventDefault();
        nextIndex = currentIndex > 0 ? currentIndex - 1 : tabs.length - 1;
      } else if (event.key === 'ArrowRight') {
        event.preventDefault();
        nextIndex = currentIndex < tabs.length - 1 ? currentIndex + 1 : 0;
      }
    } else {
      if (event.key === 'ArrowUp') {
        event.preventDefault();
        nextIndex = currentIndex > 0 ? currentIndex - 1 : tabs.length - 1;
      } else if (event.key === 'ArrowDown') {
        event.preventDefault();
        nextIndex = currentIndex < tabs.length - 1 ? currentIndex + 1 : 0;
      }
    }

    if (nextIndex !== currentIndex) {
      tabs[nextIndex]?.focus();
      tabs[nextIndex]?.click();
    }
  };

  return (
    <div
      role="tablist"
      aria-orientation={orientation}
      onKeyDown={handleKeyDown}
      className={`
        ${orientation === 'horizontal'
          ? 'flex border-b border-gray-200'
          : 'flex flex-col border-r border-gray-200 min-w-[200px]'
        }
        ${className}
      `}
    >
      {children}
    </div>
  );
};

export interface TabProps {
  /** Tab value */
  value: string;
  /** Tab label */
  children: React.ReactNode;
  /** Disabled state */
  disabled?: boolean;
  /** Custom className */
  className?: string;
}

export const Tab: React.FC<TabProps> = ({
  value,
  children,
  disabled = false,
  className = '',
}) => {
  const { activeTab, setActiveTab, orientation } = useTabsContext();
  const isActive = activeTab === value;

  return (
    <button
      role="tab"
      type="button"
      aria-selected={isActive}
      aria-controls={`panel-${value}`}
      id={`tab-${value}`}
      tabIndex={isActive ? 0 : -1}
      disabled={disabled}
      onClick={() => !disabled && setActiveTab(value)}
      className={`
        relative px-4 py-2 text-sm font-medium transition-colors
        focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
        disabled:opacity-50 disabled:cursor-not-allowed
        ${orientation === 'horizontal'
          ? `border-b-2 ${
              isActive
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`
          : `border-r-2 text-left ${
              isActive
                ? 'border-primary-600 text-primary-600 bg-primary-50'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:bg-gray-50'
            }`
        }
        ${className}
      `}
    >
      {children}
    </button>
  );
};

export interface TabPanelsProps {
  /** Children */
  children: React.ReactNode;
  /** Custom className */
  className?: string;
}

export const TabPanels: React.FC<TabPanelsProps> = ({ children, className = '' }) => {
  return (
    <div className={`flex-1 ${className}`}>
      {children}
    </div>
  );
};

export interface TabPanelProps {
  /** Panel value (must match Tab value) */
  value: string;
  /** Panel content */
  children: React.ReactNode;
  /** Custom className */
  className?: string;
}

export const TabPanel: React.FC<TabPanelProps> = ({
  value,
  children,
  className = '',
}) => {
  const { activeTab } = useTabsContext();
  const isActive = activeTab === value;

  if (!isActive) return null;

  return (
    <div
      role="tabpanel"
      id={`panel-${value}`}
      aria-labelledby={`tab-${value}`}
      tabIndex={0}
      className={`focus:outline-none ${className}`}
    >
      {children}
    </div>
  );
};

// Custom hook for controlled tabs
export const useTabs = (defaultValue?: string) => {
  const [activeTab, setActiveTab] = useState(defaultValue || '');

  return {
    activeTab,
    setActiveTab,
  };
};
