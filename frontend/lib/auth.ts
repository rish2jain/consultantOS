/**
 * Authentication Token Management
 * 
 * SECURITY NOTE: This module stores API keys in memory only (not in localStorage/sessionStorage)
 * to prevent XSS attacks from accessing sensitive authentication tokens.
 * 
 * IMPORTANT SECURITY CONSIDERATIONS:
 * 
 * 1. Current Implementation (In-Memory Only):
 *    - Tokens are stored in a module-level variable
 *    - Tokens are lost on page refresh (user must re-authenticate)
 *    - This is more secure than localStorage but has UX trade-offs
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

// In-memory storage for API key (lost on page refresh)
let apiKey: string | null = null;

/**
 * Set the API key (in-memory only)
 * @param key - The API key to store
 */
export function setApiKey(key: string): void {
  apiKey = key;
}

/**
 * Get the API key (from memory only)
 * @returns The API key or null if not set
 */
export function getApiKey(): string | null {
  return apiKey;
}

/**
 * Clear the API key from memory
 */
export function clearApiKey(): void {
  apiKey = null;
}

/**
 * Check if an API key is currently stored
 * @returns True if an API key exists, false otherwise
 */
export function hasApiKey(): boolean {
  return apiKey !== null;
}

