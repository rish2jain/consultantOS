"use client";

import { useRouter } from 'next/navigation';
import { useKeyboardShortcuts, commonShortcuts } from '@/app/hooks/useKeyboardShortcuts';

/**
 * Global keyboard shortcuts component
 * Adds common shortcuts across the application
 */
export function KeyboardShortcuts() {
  const router = useRouter();

  useKeyboardShortcuts({
    shortcuts: [
      commonShortcuts.goToDashboard(router),
      commonShortcuts.goToReports(router),
      commonShortcuts.createAnalysis(router),
      commonShortcuts.goToTemplates(router),
      commonShortcuts.goToJobs(router),
      commonShortcuts.search(router),
    ],
    enabled: true,
  });

  return null; // This component doesn't render anything
}

