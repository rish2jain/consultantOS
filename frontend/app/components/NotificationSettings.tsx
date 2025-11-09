"use client";

import React, { useEffect, useState, useRef } from "react";
import { Bell, Mail, Clock, Save, X } from "lucide-react";
import { Button } from "./Button";
import { Alert } from "./Alert";
import { Spinner } from "./Spinner";
import { Card } from "./Card";

export interface NotificationPreferences {
  new_comments: boolean;
  comment_replies: boolean;
  report_shared: boolean;
  new_versions: boolean;
  analysis_complete: boolean;
  email_enabled: boolean;
  email_frequency: "instant" | "daily" | "weekly";
}

export interface NotificationSettingsProps {
  /** User ID */
  userId: string;
  /** Current settings (optional for initial load) */
  currentSettings?: NotificationPreferences;
  /** Update handler */
  onUpdate?: (settings: NotificationPreferences) => void;
  /** API base URL */
  apiBaseUrl?: string;
}

const DEFAULT_SETTINGS: NotificationPreferences = {
  new_comments: true,
  comment_replies: true,
  report_shared: true,
  new_versions: true,
  analysis_complete: true,
  email_enabled: false,
  email_frequency: "instant",
};

export const NotificationSettings: React.FC<NotificationSettingsProps> = ({
  userId,
  currentSettings,
  onUpdate,
  apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080",
}) => {
  const [settings, setSettings] = useState<NotificationPreferences>(
    currentSettings || DEFAULT_SETTINGS
  );
  const [originalSettings, setOriginalSettings] =
    useState<NotificationPreferences>(currentSettings || DEFAULT_SETTINGS);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const successTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Fetch current settings
  useEffect(() => {
    const fetchSettings = async () => {
      if (currentSettings) return; // Skip if settings provided

      setIsLoading(true);
      setError(null);

      try {
        const response = await fetch(
          `${apiBaseUrl}/notifications/settings?user_id=${userId}`,
          {
            headers: {
              "Content-Type": "application/json",
            },
          }
        );

        if (!response.ok) {
          throw new Error("Failed to fetch notification settings");
        }

        const data = await response.json();
        setSettings(data.settings || DEFAULT_SETTINGS);
        setOriginalSettings(data.settings || DEFAULT_SETTINGS);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to load settings"
        );
        console.error("Error fetching notification settings:", err);
      } finally {
        setIsLoading(false);
      }
    };

    if (userId) {
      fetchSettings();
    }
  }, [userId, currentSettings, apiBaseUrl]);

  // Toggle notification type
  const handleToggle = (key: keyof NotificationPreferences) => {
    setSettings((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
    setSuccess(false);
  };

  // Change email frequency
  const handleFrequencyChange = (frequency: "instant" | "daily" | "weekly") => {
    setSettings((prev) => ({
      ...prev,
      email_frequency: frequency,
    }));
    setSuccess(false);
  };

  // Save settings
  const handleSave = async () => {
    setIsSaving(true);
    setError(null);
    setSuccess(false);

    try {
      const response = await fetch(`${apiBaseUrl}/notifications/settings`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: userId,
          settings,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to update notification settings");
      }

      const data = await response.json();
      setSettings(data.settings || settings);
      setOriginalSettings(data.settings || settings);
      setSuccess(true);

      if (onUpdate) {
        onUpdate(data.settings || settings);
      }

      // Clear any existing timeout
      if (successTimeoutRef.current) {
        clearTimeout(successTimeoutRef.current);
      }

      // Auto-hide success message after 3 seconds
      successTimeoutRef.current = setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save settings");
      console.error("Error saving notification settings:", err);
    } finally {
      setIsSaving(false);
    }
  };

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (successTimeoutRef.current) {
        clearTimeout(successTimeoutRef.current);
      }
    };
  }, []);

  // Cancel changes
  const handleCancel = () => {
    setSettings(originalSettings);
    setSuccess(false);
    setError(null);
    // Clear timeout when canceling
    if (successTimeoutRef.current) {
      clearTimeout(successTimeoutRef.current);
    }
  };

  // Check if settings changed
  const hasChanges =
    JSON.stringify(settings) !== JSON.stringify(originalSettings);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-12">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">
          Notification Settings
        </h2>
        <p className="text-sm text-gray-600 mt-1">
          Manage how and when you receive notifications
        </p>
      </div>

      {/* Alerts */}
      {error && (
        <Alert
          variant="error"
          title="Error"
          description={error}
          dismissible
          onClose={() => setError(null)}
        />
      )}

      {success && (
        <Alert
          variant="success"
          title="Settings saved"
          description="Your notification preferences have been updated successfully."
          dismissible
          onClose={() => setSuccess(false)}
          autoDismiss={3000}
        />
      )}

      {/* Notification Types */}
      <Card>
        <div className="p-6 space-y-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center">
              <Bell className="w-5 h-5 text-primary-600" aria-hidden="true" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">
                In-App Notifications
              </h3>
              <p className="text-sm text-gray-600">
                Choose which activities trigger notifications
              </p>
            </div>
          </div>

          <div className="space-y-4">
            {/* New Comments */}
            <div className="flex items-center justify-between py-3 border-b border-gray-100">
              <div className="flex-1">
                <label
                  htmlFor="new_comments"
                  className="text-sm font-medium text-gray-900"
                >
                  New comments on my reports
                </label>
                <p className="text-sm text-gray-600">
                  Get notified when someone comments on your reports
                </p>
              </div>
              <button
                id="new_comments"
                type="button"
                role="switch"
                aria-checked={settings.new_comments}
                onClick={() => handleToggle("new_comments")}
                className={`
                  relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full
                  border-2 border-transparent transition-colors duration-200 ease-in-out
                  focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
                  ${settings.new_comments ? "bg-primary-600" : "bg-gray-200"}
                `}
              >
                <span
                  className={`
                    pointer-events-none inline-block h-5 w-5 transform rounded-full
                    bg-white shadow ring-0 transition duration-200 ease-in-out
                    ${settings.new_comments ? "translate-x-5" : "translate-x-0"}
                  `}
                />
              </button>
            </div>

            {/* Comment Replies */}
            <div className="flex items-center justify-between py-3 border-b border-gray-100">
              <div className="flex-1">
                <label
                  htmlFor="comment_replies"
                  className="text-sm font-medium text-gray-900"
                >
                  Replies to my comments
                </label>
                <p className="text-sm text-gray-600">
                  Get notified when someone replies to your comments
                </p>
              </div>
              <button
                id="comment_replies"
                type="button"
                role="switch"
                aria-checked={settings.comment_replies}
                onClick={() => handleToggle("comment_replies")}
                className={`
                  relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full
                  border-2 border-transparent transition-colors duration-200 ease-in-out
                  focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
                  ${settings.comment_replies ? "bg-primary-600" : "bg-gray-200"}
                `}
              >
                <span
                  className={`
                    pointer-events-none inline-block h-5 w-5 transform rounded-full
                    bg-white shadow ring-0 transition duration-200 ease-in-out
                    ${
                      settings.comment_replies
                        ? "translate-x-5"
                        : "translate-x-0"
                    }
                  `}
                />
              </button>
            </div>

            {/* Report Shared */}
            <div className="flex items-center justify-between py-3 border-b border-gray-100">
              <div className="flex-1">
                <label
                  htmlFor="report_shared"
                  className="text-sm font-medium text-gray-900"
                >
                  Report shared with me
                </label>
                <p className="text-sm text-gray-600">
                  Get notified when someone shares a report with you
                </p>
              </div>
              <button
                id="report_shared"
                type="button"
                role="switch"
                aria-checked={settings.report_shared}
                onClick={() => handleToggle("report_shared")}
                className={`
                  relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full
                  border-2 border-transparent transition-colors duration-200 ease-in-out
                  focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
                  ${settings.report_shared ? "bg-primary-600" : "bg-gray-200"}
                `}
              >
                <span
                  className={`
                    pointer-events-none inline-block h-5 w-5 transform rounded-full
                    bg-white shadow ring-0 transition duration-200 ease-in-out
                    ${
                      settings.report_shared ? "translate-x-5" : "translate-x-0"
                    }
                  `}
                />
              </button>
            </div>

            {/* New Versions */}
            <div className="flex items-center justify-between py-3 border-b border-gray-100">
              <div className="flex-1">
                <label
                  htmlFor="new_versions"
                  className="text-sm font-medium text-gray-900"
                >
                  New report versions
                </label>
                <p className="text-sm text-gray-600">
                  Get notified when reports you follow are updated
                </p>
              </div>
              <button
                id="new_versions"
                type="button"
                role="switch"
                aria-checked={settings.new_versions}
                onClick={() => handleToggle("new_versions")}
                className={`
                  relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full
                  border-2 border-transparent transition-colors duration-200 ease-in-out
                  focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
                  ${settings.new_versions ? "bg-primary-600" : "bg-gray-200"}
                `}
              >
                <span
                  className={`
                    pointer-events-none inline-block h-5 w-5 transform rounded-full
                    bg-white shadow ring-0 transition duration-200 ease-in-out
                    ${settings.new_versions ? "translate-x-5" : "translate-x-0"}
                  `}
                />
              </button>
            </div>

            {/* Analysis Complete */}
            <div className="flex items-center justify-between py-3">
              <div className="flex-1">
                <label
                  htmlFor="analysis_complete"
                  className="text-sm font-medium text-gray-900"
                >
                  Analysis completion
                </label>
                <p className="text-sm text-gray-600">
                  Get notified when your analysis jobs are complete
                </p>
              </div>
              <button
                id="analysis_complete"
                type="button"
                role="switch"
                aria-checked={settings.analysis_complete}
                onClick={() => handleToggle("analysis_complete")}
                className={`
                  relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full
                  border-2 border-transparent transition-colors duration-200 ease-in-out
                  focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
                  ${
                    settings.analysis_complete
                      ? "bg-primary-600"
                      : "bg-gray-200"
                  }
                `}
              >
                <span
                  className={`
                    pointer-events-none inline-block h-5 w-5 transform rounded-full
                    bg-white shadow ring-0 transition duration-200 ease-in-out
                    ${
                      settings.analysis_complete
                        ? "translate-x-5"
                        : "translate-x-0"
                    }
                  `}
                />
              </button>
            </div>
          </div>
        </div>
      </Card>

      {/* Email Notifications */}
      <Card>
        <div className="p-6 space-y-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
              <Mail className="w-5 h-5 text-blue-600" aria-hidden="true" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">
                Email Notifications
              </h3>
              <p className="text-sm text-gray-600">
                Receive notifications via email
              </p>
            </div>
          </div>

          <div className="space-y-4">
            {/* Email Toggle */}
            <div className="flex items-center justify-between py-3 border-b border-gray-100">
              <div className="flex-1">
                <label
                  htmlFor="email_enabled"
                  className="text-sm font-medium text-gray-900"
                >
                  Enable email notifications
                </label>
                <p className="text-sm text-gray-600">
                  Receive notifications in your inbox
                </p>
              </div>
              <button
                id="email_enabled"
                type="button"
                role="switch"
                aria-checked={settings.email_enabled}
                onClick={() => handleToggle("email_enabled")}
                className={`
                  relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full
                  border-2 border-transparent transition-colors duration-200 ease-in-out
                  focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
                  ${settings.email_enabled ? "bg-primary-600" : "bg-gray-200"}
                `}
              >
                <span
                  className={`
                    pointer-events-none inline-block h-5 w-5 transform rounded-full
                    bg-white shadow ring-0 transition duration-200 ease-in-out
                    ${
                      settings.email_enabled ? "translate-x-5" : "translate-x-0"
                    }
                  `}
                />
              </button>
            </div>

            {/* Email Frequency */}
            {settings.email_enabled && (
              <div className="py-3">
                <div className="flex items-center gap-2 mb-3">
                  <Clock className="w-4 h-4 text-gray-600" aria-hidden="true" />
                  <label className="text-sm font-medium text-gray-900">
                    Email frequency
                  </label>
                </div>
                <div className="space-y-2">
                  {(["instant", "daily", "weekly"] as const).map(
                    (frequency) => (
                      <button
                        key={frequency}
                        type="button"
                        onClick={() => handleFrequencyChange(frequency)}
                        className={`
                        w-full flex items-center justify-between px-4 py-3 border rounded-lg
                        transition-colors
                        ${
                          settings.email_frequency === frequency
                            ? "border-primary-500 bg-primary-50"
                            : "border-gray-200 hover:border-gray-300 hover:bg-gray-50"
                        }
                        focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
                      `}
                      >
                        <div className="text-left">
                          <p className="text-sm font-medium text-gray-900 capitalize">
                            {frequency}
                          </p>
                          <p className="text-sm text-gray-600">
                            {frequency === "instant" &&
                              "Get emails immediately when notifications arrive"}
                            {frequency === "daily" &&
                              "Receive a daily digest of notifications"}
                            {frequency === "weekly" &&
                              "Receive a weekly summary of notifications"}
                          </p>
                        </div>
                        <div
                          className={`
                          w-5 h-5 rounded-full border-2 flex items-center justify-center
                          ${
                            settings.email_frequency === frequency
                              ? "border-primary-600 bg-primary-600"
                              : "border-gray-300"
                          }
                        `}
                          aria-hidden="true"
                        >
                          {settings.email_frequency === frequency && (
                            <div className="w-2 h-2 rounded-full bg-white" />
                          )}
                        </div>
                      </button>
                    )
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </Card>

      {/* Actions */}
      {hasChanges && (
        <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-200">
          <Button
            variant="outline"
            onClick={handleCancel}
            disabled={isSaving}
            leftIcon={<X className="w-4 h-4" />}
          >
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={handleSave}
            isLoading={isSaving}
            leftIcon={<Save className="w-4 h-4" />}
          >
            Save Changes
          </Button>
        </div>
      )}
    </div>
  );
};
