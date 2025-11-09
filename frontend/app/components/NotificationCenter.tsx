"use client";

import React, { useEffect, useRef, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Bell, Check, Trash2, Inbox } from "lucide-react";
import { Badge } from "./Badge";
import { Button } from "./Button";
import { Spinner } from "./Spinner";
import { Alert } from "./Alert";
import { NotificationItem, Notification } from "./NotificationItem";

export interface NotificationCenterProps {
  /** User ID to fetch notifications for */
  userId: string;
  /** Polling interval in milliseconds (default: 30000 = 30s) */
  pollingInterval?: number;
  /** API base URL */
  apiBaseUrl?: string;
}

interface NotificationGroup {
  label: string;
  notifications: Notification[];
}

export const NotificationCenter: React.FC<NotificationCenterProps> = ({
  userId,
  pollingInterval = 30000,
  apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080",
}) => {
  const router = useRouter();
  const [isOpen, setIsOpen] = useState(false);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);

  // Fetch notifications
  const fetchNotifications = useCallback(async () => {
    try {
      setError(null);
      const response = await fetch(
        `${apiBaseUrl}/notifications?user_id=${userId}`,
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      if (!response.ok) {
        throw new Error("Failed to fetch notifications");
      }

      const data = await response.json();
      setNotifications(data.notifications || []);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load notifications"
      );
      console.error("Error fetching notifications:", err);
    } finally {
      setIsLoading(false);
    }
  }, [userId, apiBaseUrl]);

  // Initial load
  useEffect(() => {
    if (userId) {
      setIsLoading(true);
      fetchNotifications();
    }
  }, [userId, fetchNotifications]);

  // Polling
  useEffect(() => {
    if (!userId || !pollingInterval) return;

    const interval = setInterval(() => {
      fetchNotifications();
    }, pollingInterval);

    return () => clearInterval(interval);
  }, [userId, pollingInterval, fetchNotifications]);

  // Close on click outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isOpen]);

  // Close on Escape key
  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setIsOpen(false);
        buttonRef.current?.focus();
      }
    };

    if (isOpen) {
      document.addEventListener("keydown", handleEscape);
    }

    return () => {
      document.removeEventListener("keydown", handleEscape);
    };
  }, [isOpen]);

  // Mark as read (optimistic update)
  const handleMarkAsRead = async (id: string) => {
    // Optimistic update
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, read: true } : n))
    );

    try {
      const response = await fetch(`${apiBaseUrl}/notifications/${id}/read`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        // Revert on error
        setNotifications((prev) =>
          prev.map((n) => (n.id === id ? { ...n, read: false } : n))
        );
        throw new Error("Failed to mark as read");
      }
    } catch (err) {
      console.error("Error marking notification as read:", err);
    }
  };

  // Mark all as read
  const handleMarkAllAsRead = async () => {
    const unreadIds = notifications.filter((n) => !n.read).map((n) => n.id);
    if (unreadIds.length === 0) return;

    // Optimistic update
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));

    try {
      const response = await fetch(`${apiBaseUrl}/notifications/read-all`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ user_id: userId }),
      });

      if (!response.ok) {
        // Revert on error
        fetchNotifications();
        throw new Error("Failed to mark all as read");
      }
    } catch (err) {
      console.error("Error marking all as read:", err);
    }
  };

  // Delete notification
  const handleDelete = async (id: string) => {
    // Optimistic update
    setNotifications((prev) => prev.filter((n) => n.id !== id));

    try {
      const response = await fetch(`${apiBaseUrl}/notifications/${id}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        // Revert on error
        fetchNotifications();
        throw new Error("Failed to delete notification");
      }
    } catch (err) {
      console.error("Error deleting notification:", err);
    }
  };

  // Clear all notifications
  const handleClearAll = async () => {
    if (!confirm("Are you sure you want to clear all notifications?")) return;

    // Optimistic update
    const previousNotifications = [...notifications];
    setNotifications([]);

    try {
      const response = await fetch(`${apiBaseUrl}/notifications/clear-all`, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ user_id: userId }),
      });

      if (!response.ok) {
        // Revert on error
        setNotifications(previousNotifications);
        throw new Error("Failed to clear notifications");
      }
    } catch (err) {
      console.error("Error clearing notifications:", err);
    }
  };

  // Click notification handler
  const handleNotificationClick = (notification: Notification) => {
    if (!notification.link) return;

    // Use Next.js router for internal routes
    if (notification.link.startsWith("/")) {
      // Internal route - use Next.js router for client-side navigation
      router.push(notification.link);
    } else {
      // External URL - validate protocol
      try {
        const url = new URL(notification.link);
        if (url.protocol === "http:" || url.protocol === "https:") {
          window.location.assign(notification.link);
        } else {
          console.error("Invalid URL protocol:", url.protocol);
        }
      } catch (err) {
        console.error("Invalid URL:", notification.link);
      }
    }
  };

  // Group notifications
  const groupNotifications = (): NotificationGroup[] => {
    const now = new Date();
    const todayStart = new Date(
      now.getFullYear(),
      now.getMonth(),
      now.getDate()
    );
    const weekStart = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);

    const unread = notifications.filter((n) => !n.read);
    const today = notifications.filter((n) => {
      const date = new Date(n.created_at);
      return n.read && date >= todayStart;
    });
    const thisWeek = notifications.filter((n) => {
      const date = new Date(n.created_at);
      return n.read && date >= weekStart && date < todayStart;
    });
    const earlier = notifications.filter((n) => {
      const date = new Date(n.created_at);
      return n.read && date < weekStart;
    });

    const groups: NotificationGroup[] = [];
    if (unread.length > 0)
      groups.push({ label: "Unread", notifications: unread });
    if (today.length > 0) groups.push({ label: "Today", notifications: today });
    if (thisWeek.length > 0)
      groups.push({ label: "This Week", notifications: thisWeek });
    if (earlier.length > 0)
      groups.push({ label: "Earlier", notifications: earlier });

    return groups;
  };

  const unreadCount = notifications.filter((n) => !n.read).length;
  const groups = groupNotifications();

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Trigger Button */}
      <button
        ref={buttonRef}
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="
          relative p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100
          rounded-full transition-colors
          focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
        "
        aria-label={`Notifications${
          unreadCount > 0 ? ` (${unreadCount} unread)` : ""
        }`}
        aria-expanded={isOpen}
        aria-haspopup="true"
      >
        <Bell className="w-6 h-6" aria-hidden="true" />
        {unreadCount > 0 && (
          <span className="absolute top-0 right-0 flex items-center justify-center">
            <Badge variant="danger" size="sm" className="min-w-[20px] h-5">
              {unreadCount > 99 ? "99+" : unreadCount}
            </Badge>
          </span>
        )}
      </button>

      {/* Dropdown Panel */}
      {isOpen && (
        <div
          className="
            absolute right-0 top-full mt-2 w-96 bg-white border border-gray-200
            rounded-lg shadow-lg z-50 max-h-[600px] flex flex-col
          "
          role="dialog"
          aria-label="Notifications panel"
        >
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">
              Notifications
            </h2>
            <div className="flex items-center gap-2">
              {unreadCount > 0 && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleMarkAllAsRead}
                  leftIcon={<Check className="w-4 h-4" />}
                  aria-label="Mark all as read"
                >
                  Mark all read
                </Button>
              )}
              {notifications.length > 0 && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleClearAll}
                  leftIcon={<Trash2 className="w-4 h-4" />}
                  aria-label="Clear all notifications"
                >
                  Clear all
                </Button>
              )}
            </div>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto">
            {isLoading && notifications.length === 0 ? (
              <div className="flex items-center justify-center p-8">
                <Spinner size="lg" />
              </div>
            ) : error ? (
              <div className="p-4">
                <Alert
                  variant="error"
                  title="Error loading notifications"
                  description={error}
                  dismissible
                  onClose={() => setError(null)}
                />
              </div>
            ) : notifications.length === 0 ? (
              <div className="flex flex-col items-center justify-center p-12 text-center">
                <div className="w-16 h-16 rounded-full bg-gray-100 flex items-center justify-center mb-4">
                  <Inbox className="w-8 h-8 text-gray-400" aria-hidden="true" />
                </div>
                <h3 className="text-sm font-medium text-gray-900 mb-1">
                  No notifications
                </h3>
                <p className="text-sm text-gray-500">
                  You're all caught up! We'll notify you when something happens.
                </p>
              </div>
            ) : (
              <div>
                {groups.map((group, index) => (
                  <div key={group.label}>
                    <div className="px-4 py-2 bg-gray-50 border-b border-gray-100">
                      <h3 className="text-xs font-semibold text-gray-700 uppercase tracking-wide">
                        {group.label}
                      </h3>
                    </div>
                    {group.notifications.map((notification) => (
                      <NotificationItem
                        key={notification.id}
                        notification={notification}
                        onRead={handleMarkAsRead}
                        onClick={handleNotificationClick}
                        onDelete={handleDelete}
                      />
                    ))}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
