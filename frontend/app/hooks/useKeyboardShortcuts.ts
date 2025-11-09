"use client";

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export interface KeyboardShortcut {
  key: string;
  ctrlKey?: boolean;
  metaKey?: boolean;
  shiftKey?: boolean;
  altKey?: boolean;
  action: () => void;
  description: string;
}

export interface UseKeyboardShortcutsOptions {
  shortcuts: KeyboardShortcut[];
  enabled?: boolean;
  preventDefault?: boolean;
}

/**
 * Hook for handling keyboard shortcuts globally
 * 
 * @example
 * ```tsx
 * useKeyboardShortcuts({
 *   shortcuts: [
 *     {
 *       key: 'k',
 *       metaKey: true,
 *       action: () => router.push('/reports'),
 *       description: 'Go to Reports'
 *     },
 *     {
 *       key: 'n',
 *       metaKey: true,
 *       shiftKey: true,
 *       action: () => router.push('/analysis'),
 *       description: 'Create New Analysis'
 *     }
 *   ]
 * });
 * ```
 */
export function useKeyboardShortcuts({
  shortcuts,
  enabled = true,
  preventDefault = true,
}: UseKeyboardShortcutsOptions) {
  useEffect(() => {
    if (!enabled || shortcuts.length === 0) return;

    const handleKeyDown = (event: KeyboardEvent) => {
      // Don't trigger shortcuts when user is typing in inputs, textareas, or contenteditable
      const target = event.target as HTMLElement;
      if (
        target.tagName === 'INPUT' ||
        target.tagName === 'TEXTAREA' ||
        target.isContentEditable
      ) {
        return;
      }

      for (const shortcut of shortcuts) {
        const keyMatch = event.key.toLowerCase() === shortcut.key.toLowerCase();
        const ctrlMatch = shortcut.ctrlKey ? event.ctrlKey : !event.ctrlKey;
        const metaMatch = shortcut.metaKey ? event.metaKey : !event.metaKey;
        const shiftMatch = shortcut.shiftKey !== undefined
          ? (shortcut.shiftKey ? event.shiftKey : !event.shiftKey)
          : true;
        const altMatch = shortcut.altKey !== undefined
          ? (shortcut.altKey ? event.altKey : !event.altKey)
          : true;

        if (keyMatch && ctrlMatch && metaMatch && shiftMatch && altMatch) {
          if (preventDefault) {
            event.preventDefault();
          }
          shortcut.action();
          break;
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [shortcuts, enabled, preventDefault]);
}

/**
 * Common keyboard shortcuts for ConsultantOS
 */
export const commonShortcuts = {
  goToReports: (router: ReturnType<typeof useRouter>) => ({
    key: 'k',
    metaKey: true,
    action: () => router.push('/reports'),
    description: 'Go to Reports',
  }),
  createAnalysis: (router: ReturnType<typeof useRouter>) => ({
    key: 'n',
    metaKey: true,
    shiftKey: true,
    action: () => router.push('/analysis'),
    description: 'Create New Analysis',
  }),
  goToDashboard: (router: ReturnType<typeof useRouter>) => ({
    key: 'd',
    metaKey: true,
    action: () => router.push('/'),
    description: 'Go to Dashboard',
  }),
  goToTemplates: (router: ReturnType<typeof useRouter>) => ({
    key: 't',
    metaKey: true,
    action: () => router.push('/templates'),
    description: 'Go to Templates',
  }),
  goToJobs: (router: ReturnType<typeof useRouter>) => ({
    key: 'j',
    metaKey: true,
    action: () => router.push('/jobs'),
    description: 'Go to Jobs',
  }),
  search: (router: ReturnType<typeof useRouter>) => ({
    key: '/',
    metaKey: true,
    action: () => router.push('/reports'),
    description: 'Search Reports',
  }),
};

