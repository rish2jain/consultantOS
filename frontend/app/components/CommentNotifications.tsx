"use client";

import React, { useState, useEffect, useRef, useCallback } from "react";
import { Bell, Check, X, ExternalLink } from "lucide-react";
import { Badge } from "./Badge";
import { Button } from "./Button";
import { Alert } from "./Alert";
import { Spinner } from "./Spinner";
import { getRelativeTime } from "../utils/dateFormat";
import * as notificationAPI from "../api/notifications";

export interface CommentNotification {
  id: string;
  type: "comment" | "reply" | "mention";
  comment: {
    id: string;
    text: string;
    user: {
      name: string;
    };
    created_at: string;
  };
  report: {
    id: string;
    title: string;
    company: string;
  };
  read: boolean;
}

export interface CommentNotificationsProps {
  /** User ID to fetch notifications for */
  userId: string;
  /** Polling interval in milliseconds */
  pollingInterval?: number;
  /** Navigation handler */
  onNavigate?: (reportId: string) => void;
  /** API base URL */
  apiBaseUrl?: string;
}

const DEFAULT_POLLING_INTERVAL = 30000; // 30 seconds

const getNotificationText = (notification: CommentNotification): string => {
  const userName = notification.comment.user.name;
  const reportTitle = `${notification.report.company} Analysis`;

  switch (notification.type) {
    case "reply":
      return `${userName} replied to your comment on "${reportTitle}"`;
    case "mention":
      return `${userName} mentioned you in "${reportTitle}"`;
    case "comment":
    default:
      return `${userName} commented on "${reportTitle}"`;
  }
};

export const CommentNotifications: React.FC<CommentNotificationsProps> = ({
  userId,
  pollingInterval = DEFAULT_POLLING_INTERVAL,
  onNavigate,
  apiBaseUrl = "/api",
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [notifications, setNotifications] = useState<CommentNotification[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const pollingTimerRef = useRef<NodeJS.Timeout>();

  const unreadCount = notifications.filter((n) => !n.read).length;

  // Fetch notifications
  const fetchNotificationsData = useCallback(async () => {
    if (!userId) return;

    try {
      setError(null);
      const data = await notificationAPI.fetchNotifications(userId, apiBaseUrl);
      // Filter to comment notifications only
      const commentNotifications = data.filter(
        (n: notificationAPI.Notification) =>
          n.type === "comment" || n.type === "reply" || n.type === "mention"
      ) as CommentNotification[];
      setNotifications(commentNotifications);
    } catch (err) {
      console.error("Error fetching notifications:", err);
      setError(
        err instanceof Error ? err.message : "Failed to load notifications"
      );
    }
  }, [userId, apiBaseUrl]);

  // Initial fetch
  useEffect(() => {
    setIsLoading(true);
    fetchNotificationsData().finally(() => setIsLoading(false));
  }, [fetchNotificationsData]);

  // Set up polling
  useEffect(() => {
    if (pollingInterval > 0) {
      pollingTimerRef.current = setInterval(
        fetchNotificationsData,
        pollingInterval
      );
    }

    return () => {
      if (pollingTimerRef.current) {
        clearInterval(pollingTimerRef.current);
      }
    };
  }, [pollingInterval, userId]);

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

  // Mark notification as read
  const markAsRead = async (notificationId: string) => {
    try {
      await notificationAPI.markAsRead(notificationId, apiBaseUrl);
      setNotifications((prev) =>
        prev.map((n) => (n.id === notificationId ? { ...n, read: true } : n))
      );
    } catch (err) {
      console.error("Error marking notification as read:", err);
    }
  };

  // Mark all as read
  const markAllAsRead = async () => {
    try {
      await notificationAPI.markAllAsRead(userId, apiBaseUrl);
      setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
    } catch (err) {
      console.error("Error marking all as read:", err);
      setError("Failed to mark all as read");
    }
  };

  // Clear all notifications
  const clearAll = async () => {
    try {
      await notificationAPI.clearAll(userId, apiBaseUrl);
      setNotifications([]);
      setIsOpen(false);
    } catch (err) {
      console.error("Error clearing notifications:", err);
      setError("Failed to clear notifications");
    }
  };

  // Navigate to report
  const handleNotificationClick = (notification: CommentNotification) => {
    markAsRead(notification.id);

    if (onNavigate) {
      onNavigate(notification.report.id);
    }

    setIsOpen(false);
  };

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Bell button */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
        aria-label={`Notifications${
          unreadCount > 0 ? `, ${unreadCount} unread` : ""
        }`}
        aria-haspopup="true"
        aria-expanded={isOpen}
      >
        <Bell className="w-6 h-6" aria-hidden="true" />

        {unreadCount > 0 && (
          <Badge
            variant="danger"
            size="sm"
            className="absolute -top-1 -right-1 min-w-[1.25rem] h-5 flex items-center justify-center px-1"
            aria-label={`${unreadCount} unread notifications`}
          >
            {unreadCount > 99 ? "99+" : unreadCount}
          </Badge>
        )}
      </button>

      {/* Dropdown panel */}
      {isOpen && (
        <div
          className="absolute right-0 top-full mt-2 w-96 bg-white border border-gray-200 rounded-lg shadow-lg z-50"
          role="menu"
          aria-orientation="vertical"
        >
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200">
            <h3 className="text-sm font-semibold text-gray-900">
              Notifications
              {unreadCount > 0 && (
                <span className="ml-2 text-gray-500 font-normal">
                  ({unreadCount} new)
                </span>
              )}
            </h3>

            <button
              type="button"
              onClick={() => setIsOpen(false)}
              className="text-gray-400 hover:text-gray-600 transition-colors"
              aria-label="Close notifications"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Actions */}
          {notifications.length > 0 && (
            <div className="flex items-center gap-2 px-4 py-2 bg-gray-50 border-b border-gray-200">
              {unreadCount > 0 && (
                <Button
                  variant="ghost"
                  size="sm"
                  leftIcon={<Check className="w-4 h-4" />}
                  onClick={markAllAsRead}
                >
                  Mark all read
                </Button>
              )}

              <Button
                variant="ghost"
                size="sm"
                onClick={clearAll}
                className="ml-auto"
              >
                Clear all
              </Button>
            </div>
          )}

          {/* Content */}
          <div className="max-h-96 overflow-y-auto">
            {isLoading ? (
              <div className="flex items-center justify-center py-8">
                <Spinner size="md" label="Loading notifications..." />
              </div>
            ) : error ? (
              <div className="p-4">
                <Alert
                  variant="error"
                  description={error}
                  dismissible
                  onClose={() => setError(null)}
                />
              </div>
            ) : notifications.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <Bell
                  className="w-12 h-12 text-gray-300 mx-auto mb-2"
                  aria-hidden="true"
                />
                <p className="text-sm">No notifications</p>
              </div>
            ) : (
              <div role="list">
                {notifications.map((notification) => (
                  <button
                    key={notification.id}
                    type="button"
                    role="menuitem"
                    onClick={() => handleNotificationClick(notification)}
                    className={`
                      w-full text-left px-4 py-3 border-b border-gray-100
                      hover:bg-gray-50 transition-colors focus:outline-none focus:bg-gray-50
                      ${!notification.read ? "bg-primary-50" : ""}
                    `}
                  >
                    <div className="flex items-start gap-3">
                      {!notification.read && (
                        <span
                          className="flex-shrink-0 w-2 h-2 mt-2 bg-primary-600 rounded-full"
                          aria-label="Unread"
                        />
                      )}

                      <div className="flex-1 min-w-0">
                        <p
                          className={`text-sm ${
                            !notification.read
                              ? "font-semibold text-gray-900"
                              : "text-gray-700"
                          }`}
                        >
                          {getNotificationText(notification)}
                        </p>

                        <p className="text-xs text-gray-500 mt-1 truncate">
                          "{notification.comment.text}"
                        </p>

                        <p className="text-xs text-gray-400 mt-1">
                          {getRelativeTime(notification.comment.created_at)}
                        </p>
                      </div>

                      <ExternalLink
                        className="w-4 h-4 text-gray-400 flex-shrink-0 mt-1"
                        aria-hidden="true"
                      />
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
