"use client";

import React from 'react';
import { Skeleton } from './LoadingStates';

/**
 * Page-level loading skeleton component
 * Provides consistent loading states across pages
 */
export interface PageLoadingProps {
  /** Show header skeleton */
  showHeader?: boolean;
  /** Show sidebar skeleton */
  showSidebar?: boolean;
  /** Number of content cards to show */
  cardCount?: number;
}

export const PageLoading: React.FC<PageLoadingProps> = ({
  showHeader = true,
  showSidebar = false,
  cardCount = 3,
}) => {
  return (
    <div className="min-h-screen bg-gray-50">
      {showHeader && (
        <div className="bg-white border-b border-gray-200 p-6 mb-6">
          <div className="max-w-7xl mx-auto">
            <Skeleton height="h-8" width="w-64" className="mb-4" />
            <div className="flex gap-2">
              <Skeleton height="h-10" width="w-32" />
              <Skeleton height="h-10" width="w-32" />
            </div>
          </div>
        </div>
      )}

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className={`grid gap-6 ${showSidebar ? 'lg:grid-cols-3' : ''}`}>
          {/* Main Content */}
          <div className={showSidebar ? 'lg:col-span-2' : ''}>
            <div className="space-y-6">
              {Array.from({ length: cardCount }).map((_, i) => (
                <div key={i} className="bg-white rounded-lg shadow p-6">
                  <Skeleton height="h-6" width="w-48" className="mb-4" />
                  <Skeleton height="h-4" width="w-full" className="mb-2" />
                  <Skeleton height="h-4" width="w-5/6" className="mb-2" />
                  <Skeleton height="h-4" width="w-4/6" />
                </div>
              ))}
            </div>
          </div>

          {/* Sidebar */}
          {showSidebar && (
            <div className="lg:col-span-1">
              <div className="bg-white rounded-lg shadow p-6 space-y-4">
                <Skeleton height="h-6" width="w-32" />
                <Skeleton height="h-20" width="w-full" />
                <Skeleton height="h-20" width="w-full" />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

/**
 * Simple page loading with just spinner
 */
export const SimplePageLoading: React.FC<{ label?: string }> = ({ 
  label = "Loading..." 
}) => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
        <p className="text-gray-600" aria-live="polite">{label}</p>
      </div>
    </div>
  );
};

