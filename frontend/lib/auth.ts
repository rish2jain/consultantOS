/**
 * Authentication Token Management
 * 
 * SECURITY NOTE: This module stores API keys in memory and sessionStorage.
 * sessionStorage persists across page navigations but is cleared when the browser tab is closed,
 * providing a balance between security and user experience.
 * 
 * IMPORTANT SECURITY CONSIDERATIONS:
 * 
 * 1. Current Implementation (Memory + sessionStorage):
 *    - Tokens are stored in a module-level variable (in-memory)
 *    - Tokens are also stored in sessionStorage for persistence across page navigations
 *    - sessionStorage is cleared when the browser tab is closed (more secure than localStorage)
 *    - This provides better UX while maintaining reasonable security
 * 
 * 2. Recommended Production Solution:
 *    - Implement a Backend-for-Frontend (BFF) pattern
 *    - Store refresh tokens in HttpOnly, Secure, SameSite cookies
 *    - Keep access tokens only in memory
 *    - Use Authorization Code + PKCE flow for OAuth
 *    - Implement token refresh mechanism
 * 
 * 3. Additional Security Measures:
 *    - Implement Content Security Policy (CSP) headers
 *    - Use Subresource Integrity (SRI) for external scripts
 *    - Sanitize all user inputs to prevent XSS
 *    - Implement rate limiting on authentication endpoints
 *    - Use HTTPS only in production
 * 
 * TODO: Migrate to BFF pattern with secure cookie-based authentication
 */

// In-memory storage for API key (for fast access)
let apiKey: string | null = null;

// Initialize from sessionStorage if available (for persistence across page navigations)
if (typeof window !== 'undefined') {
  try {
    const stored = sessionStorage.getItem('api_key');
    if (stored) {
      apiKey = stored;
    }
  } catch (e) {
    // sessionStorage may not be available (e.g., in private browsing)
    console.warn('Failed to read from sessionStorage:', e);
  }
}

/**
 * Set the API key (in-memory and sessionStorage)
 * @param key - The API key to store
 */
export function setApiKey(key: string): void {
  apiKey = key;
  
  // Also store in sessionStorage for persistence across page navigations
  if (typeof window !== 'undefined') {
    try {
      sessionStorage.setItem('api_key', key);
    } catch (e) {
      // sessionStorage may not be available (e.g., in private browsing)
      console.warn('Failed to write to sessionStorage:', e);
    }
  }
}

/**
 * Get the API key (from memory, fallback to sessionStorage)
 * @returns The API key or null if not set
 */
export function getApiKey(): string | null {
  // Return from memory if available
  if (apiKey) {
    return apiKey;
  }
  
  // Fallback to sessionStorage (in case memory was cleared)
  if (typeof window !== 'undefined') {
    try {
      const stored = sessionStorage.getItem('api_key');
      if (stored) {
        apiKey = stored; // Restore to memory
        return stored;
      }
    } catch (e) {
      // sessionStorage may not be available
      console.warn('Failed to read from sessionStorage:', e);
    }
  }
  
  return null;
}

/**
 * Clear the API key from memory and sessionStorage
 */
export function clearApiKey(): void {
  apiKey = null;
  
  // Also clear from sessionStorage
  if (typeof window !== 'undefined') {
    try {
      sessionStorage.removeItem('api_key');
    } catch (e) {
      // sessionStorage may not be available
      console.warn('Failed to clear sessionStorage:', e);
    }
  }
}

/**
 * Check if an API key is currently stored
 * @returns True if an API key exists, false otherwise
 */
export function hasApiKey(): boolean {
  return apiKey !== null;
}

