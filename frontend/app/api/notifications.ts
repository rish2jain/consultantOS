/**
 * Unified notification API functions
 * Provides consistent API patterns for notification operations
 */

const DEFAULT_API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

export interface Notification {
  id: string;
  type: string;
  title: string;
  description: string;
  read: boolean;
  created_at: string;
  link?: string;
}

/**
 * Fetch notifications for a user
 */
export async function fetchNotifications(
  userId: string,
  apiBaseUrl: string = DEFAULT_API_BASE
): Promise<Notification[]> {
  // URL-encode userId to prevent injection
  const encodedUserId = encodeURIComponent(userId);
  
  // Get auth token from secure storage
  const token = typeof window !== 'undefined' 
    ? localStorage.getItem('token') || sessionStorage.getItem('token')
    : null;
  
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const response = await fetch(`${apiBaseUrl}/notifications?user_id=${encodedUserId}`, {
    headers,
  });

  if (!response.ok) {
    throw new Error('Failed to fetch notifications');
  }

  const data = await response.json();
  return data.notifications || [];
}

/**
 * Mark a notification as read
 */
export async function markAsRead(
  id: string,
  apiBaseUrl: string = DEFAULT_API_BASE
): Promise<void> {
  const response = await fetch(`${apiBaseUrl}/notifications/${id}/read`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error('Failed to mark notification as read');
  }
}

/**
 * Mark all notifications as read for a user
 */
export async function markAllAsRead(
  userId: string,
  apiBaseUrl: string = DEFAULT_API_BASE
): Promise<void> {
  const response = await fetch(`${apiBaseUrl}/notifications/read-all`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ user_id: userId }),
  });

  if (!response.ok) {
    throw new Error('Failed to mark all notifications as read');
  }
}

/**
 * Delete a notification
 */
export async function deleteNotification(
  id: string,
  apiBaseUrl: string = DEFAULT_API_BASE
): Promise<void> {
  const response = await fetch(`${apiBaseUrl}/notifications/${id}`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    throw new Error('Failed to delete notification');
  }
}

/**
 * Clear all notifications for a user
 */
export async function clearAll(
  userId: string,
  apiBaseUrl: string = DEFAULT_API_BASE
): Promise<void> {
  const response = await fetch(`${apiBaseUrl}/notifications/clear-all`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ user_id: userId }),
  });

  if (!response.ok) {
    throw new Error('Failed to clear all notifications');
  }
}

