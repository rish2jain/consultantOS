/**
 * Analysis utility functions
 * 
 * Helper functions for working with analysis data
 */

/**
 * Placeholder text patterns that indicate incomplete analysis
 * 
 * Note: These patterns are used to detect when analysis results contain
 * placeholder text rather than actual analysis content. If the backend
 * uses "Analysis completed" as a placeholder, it should be replaced with
 * a more distinctive placeholder string to avoid false positives.
 */
const PLACEHOLDER_PATTERNS = [
  'Analysis pending',
  'Data collection in progress',
  'Review recommended',
  'Data validation needed',
];

/**
 * Check if a string array contains placeholder text
 * @param items - Array of strings to check
 * @returns true if any item matches placeholder patterns
 */
export function containsPlaceholderText(items: string[] | undefined): boolean {
  if (!items || items.length === 0) {
    return false;
  }
  
  return items.some(item => 
    PLACEHOLDER_PATTERNS.some(pattern => 
      item.toLowerCase().includes(pattern.toLowerCase())
    )
  );
}

/**
 * Check if SWOT analysis contains placeholder text
 * @param swot - SWOT analysis object
 * @returns true if any SWOT category contains placeholder text
 */
export function isSWOTPlaceholder(swot: {
  strengths?: string[];
  weaknesses?: string[];
  opportunities?: string[];
  threats?: string[];
} | undefined): boolean {
  if (!swot) {
    return false;
  }
  
  return (
    containsPlaceholderText(swot.strengths) ||
    containsPlaceholderText(swot.weaknesses) ||
    containsPlaceholderText(swot.opportunities) ||
    containsPlaceholderText(swot.threats)
  );
}

/**
 * Check if Porter's analysis contains placeholder text
 * @param porter - Porter's Five Forces object
 * @returns true if analysis contains placeholder text
 */
export function isPorterPlaceholder(porter: {
  detailed_analysis?: Record<string, string>;
  overall_assessment?: string;
} | undefined): boolean {
  if (!porter) {
    return false;
  }
  
  // Check overall assessment
  if (porter.overall_assessment) {
    if (PLACEHOLDER_PATTERNS.some(pattern => 
      porter.overall_assessment!.toLowerCase().includes(pattern.toLowerCase())
    )) {
      return true;
    }
  }
  
  // Check detailed analysis values
  if (porter.detailed_analysis) {
    return Object.values(porter.detailed_analysis).some(value =>
      typeof value === 'string' && PLACEHOLDER_PATTERNS.some(pattern =>
        value.toLowerCase().includes(pattern.toLowerCase())
      )
    );
  }
  
  return false;
}

/**
 * Get a user-friendly message when placeholder text is detected
 * @param framework - Framework name (e.g., 'SWOT', 'Porter')
 * @returns User-friendly error message
 */
export function getPlaceholderMessage(framework?: string): string {
  const frameworkName = framework || 'analysis';
  return `The ${frameworkName} analysis could not be completed. This may be due to insufficient data, API issues, or processing errors. Please check the backend logs for details or try regenerating the analysis.`;
}

