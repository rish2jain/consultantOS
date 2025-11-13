"use client";

import React, { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "./Card";
import { Button } from "./Button";
import { Input } from "./Input";
import { Dropdown, DropdownItem } from "./Dropdown";
import { Alert } from "./Alert";
import { Spinner } from "./Spinner";
import { Badge } from "./Badge";
import {
  Lock,
  Calendar,
  Eye,
  Link,
  Trash2,
  Save,
  AlertTriangle,
} from "lucide-react";
import { Modal } from "./Modal";

export interface ShareSettingsProps {
  /** Share ID to manage */
  shareId: string;
  /** Current share settings */
  currentSettings?: ShareSettingsData;
  /** Update callback */
  onUpdate?: (settings: ShareSettingsData) => void;
  /** Revoke callback */
  onRevoke?: () => void;
}

export interface ShareSettingsData {
  share_id: string;
  share_link: string;
  password_protected: boolean;
  expires_at?: string;
  permissions: "view" | "download";
  created_at: string;
  access_count: number;
  is_active: boolean;
}

const EXPIRATION_OPTIONS: DropdownItem[] = [
  { label: "24 hours", value: "24h" },
  { label: "7 days", value: "7d" },
  { label: "30 days", value: "30d" },
  { label: "Never", value: "never" },
  { label: "Custom", value: "custom" },
];

const PERMISSION_OPTIONS: DropdownItem[] = [
  { label: "View only", value: "view", icon: <Eye className="w-4 h-4" /> },
  {
    label: "View & Download",
    value: "download",
    icon: <Eye className="w-4 h-4" />,
  },
];

export const ShareSettings: React.FC<ShareSettingsProps> = ({
  shareId,
  currentSettings: initialSettings,
  onUpdate,
  onRevoke,
}) => {
  const [isLoading, setIsLoading] = useState(!initialSettings);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [settings, setSettings] = useState<ShareSettingsData | null>(
    initialSettings || null
  );

  const [passwordProtected, setPasswordProtected] = useState(
    initialSettings?.password_protected || false
  );
  const [newPassword, setNewPassword] = useState("");
  const [expiration, setExpiration] = useState<string>("never");
  const [initialExpirationPreset, setInitialExpirationPreset] =
    useState<string>("never");
  const [customExpirationDate, setCustomExpirationDate] = useState<
    string | null
  >(null);
  const [permissions, setPermissions] = useState<"view" | "download">(
    initialSettings?.permissions || "view"
  );

  const [showRevokeConfirm, setShowRevokeConfirm] = useState(false);
  const [isRevoking, setIsRevoking] = useState(false);

  useEffect(() => {
    if (!initialSettings) {
      loadSettings();
    } else {
      initializeFormState(initialSettings);
    }
  }, [shareId, initialSettings]);

  const loadSettings = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/shares/${shareId}/settings`);

      if (!response.ok) {
        throw new Error("Failed to load share settings");
      }

      const data = await response.json();
      setSettings(data);
      initializeFormState(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setIsLoading(false);
    }
  };

  const initializeFormState = (data: ShareSettingsData) => {
    setPasswordProtected(data.password_protected);
    setPermissions(data.permissions);

    // Determine initial expiration preset from expires_at
    if (data.expires_at) {
      const expiresAt = new Date(data.expires_at);
      const now = new Date();
      const diffMs = expiresAt.getTime() - now.getTime();
      const diffHours = diffMs / (1000 * 60 * 60);

      let preset = "custom";
      if (diffHours <= 24.5 && diffHours >= 23.5) {
        preset = "24h";
      } else if (diffHours <= 168.5 && diffHours >= 167.5) {
        // ~7 days
        preset = "7d";
      } else if (diffHours <= 720.5 && diffHours >= 719.5) {
        // ~30 days
        preset = "30d";
      }

      setExpiration(preset);
      setInitialExpirationPreset(preset);
      setCustomExpirationDate(preset === "custom" ? data.expires_at : null);
    } else {
      setExpiration("never");
      setInitialExpirationPreset("never");
      setCustomExpirationDate(null);
    }
  };

  const calculateExpirationDate = (option: string): string | undefined => {
    if (option === "never") return undefined;
    if (option === "custom") {
      return customExpirationDate || undefined;
    }

    const now = new Date();
    if (option === "24h") {
      now.setHours(now.getHours() + 24);
    } else if (option === "7d") {
      now.setDate(now.getDate() + 7);
    } else if (option === "30d") {
      now.setDate(now.getDate() + 30);
    }

    return now.toISOString();
  };

  const handleSaveSettings = async () => {
    setIsSaving(true);
    setError(null);
    setSuccessMessage(null);

    try {
      const response = await fetch(`/api/shares/${shareId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          password: passwordProtected && newPassword ? newPassword : undefined,
          remove_password:
            passwordProtected === false && settings?.password_protected,
          expires_at: calculateExpirationDate(expiration),
          permissions,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to update settings");
      }

      const updatedData = await response.json();
      setSettings(updatedData);
      setNewPassword(""); // Clear password field after save
      setSuccessMessage("Settings updated successfully");
      onUpdate?.(updatedData);

      // Update initial state to reflect saved values
      if (updatedData.expires_at) {
        const expiresAt = new Date(updatedData.expires_at);
        const now = new Date();
        const diffMs = expiresAt.getTime() - now.getTime();
        const diffHours = diffMs / (1000 * 60 * 60);

        let preset = "custom";
        if (diffHours <= 24.5 && diffHours >= 23.5) {
          preset = "24h";
        } else if (diffHours <= 168.5 && diffHours >= 167.5) {
          preset = "7d";
        } else if (diffHours <= 720.5 && diffHours >= 719.5) {
          preset = "30d";
        }

        setInitialExpirationPreset(preset);
        setCustomExpirationDate(
          preset === "custom" ? updatedData.expires_at : null
        );
      } else {
        setInitialExpirationPreset("never");
        setCustomExpirationDate(null);
      }

      // Auto-dismiss success message
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setIsSaving(false);
    }
  };

  const handleRevoke = async () => {
    setIsRevoking(true);
    setError(null);

    try {
      const response = await fetch(`/api/shares/${shareId}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        throw new Error("Failed to revoke share");
      }

      setShowRevokeConfirm(false);
      onRevoke?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
      setShowRevokeConfirm(false);
    } finally {
      setIsRevoking(false);
    }
  };

  const handleCopyLink = async () => {
    if (!settings?.share_link) return;

    try {
      await navigator.clipboard.writeText(settings.share_link);
      setSuccessMessage("Link copied to clipboard");
      setTimeout(() => setSuccessMessage(null), 2000);
    } catch (err) {
      setError("Failed to copy link");
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  if (isLoading) {
    return (
      <Card padding="lg">
        <div className="flex items-center justify-center py-8">
          <Spinner size="lg" label="Loading settings..." />
        </div>
      </Card>
    );
  }

  if (!settings) {
    return (
      <Card padding="lg">
        <Alert
          variant="error"
          title="Error"
          description={error || "Failed to load share settings"}
        />
      </Card>
    );
  }

  // Check for expiration changes by comparing preset and custom date
  const expirationChanged =
    expiration !== initialExpirationPreset ||
    (expiration === "custom" &&
      customExpirationDate !== null &&
      settings.expires_at != null &&
      new Date(customExpirationDate).getTime() !==
        new Date(settings.expires_at).getTime()) ||
    (expiration === "custom" &&
      customExpirationDate === null &&
      settings.expires_at != null) ||
    (expiration !== "custom" &&
      settings.expires_at != null &&
      initialExpirationPreset === "custom");

  const hasChanges =
    passwordProtected !== settings.password_protected ||
    permissions !== settings.permissions ||
    (passwordProtected && newPassword.trim() !== "") ||
    expirationChanged;

  return (
    <>
      <Card padding="lg">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Share Settings</CardTitle>
            <Badge variant={settings.is_active ? "success" : "danger"} dot>
              {settings.is_active ? "Active" : "Revoked"}
            </Badge>
          </div>
        </CardHeader>

        <CardContent>
          <div className="space-y-6">
            {error && (
              <Alert
                variant="error"
                description={error}
                dismissible
                onClose={() => setError(null)}
              />
            )}

            {successMessage && (
              <Alert
                variant="success"
                description={successMessage}
                dismissible
                autoDismiss={3000}
                onClose={() => setSuccessMessage(null)}
              />
            )}

            {/* Share Link */}
            <div className="space-y-2">
              <label className="flex items-center gap-2 text-sm font-medium text-gray-700">
                <Link className="w-4 h-4" />
                Share Link
              </label>
              <div className="flex gap-2">
                <Input
                  value={settings.share_link}
                  readOnly
                  fullWidth
                  className="font-mono text-sm"
                />
                <Button onClick={handleCopyLink} variant="outline" size="md">
                  Copy
                </Button>
              </div>
            </div>

            {/* Info */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg">
              <div>
                <p className="text-xs text-gray-500 mb-1">Created</p>
                <p className="text-sm font-medium text-gray-900">
                  {formatDate(settings.created_at)}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500 mb-1">Access Count</p>
                <p className="text-sm font-medium text-gray-900">
                  {settings.access_count} views
                </p>
              </div>
            </div>

            {/* Password Protection */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <label className="flex items-center gap-2 text-sm font-medium text-gray-700">
                  <Lock className="w-4 h-4" />
                  Password Protection
                </label>
                <button
                  type="button"
                  role="switch"
                  aria-checked={passwordProtected}
                  onClick={() => setPasswordProtected(!passwordProtected)}
                  disabled={!settings.is_active}
                  className={`
                    relative inline-flex h-6 w-11 items-center rounded-full transition-colors
                    focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
                    ${passwordProtected ? "bg-primary-600" : "bg-gray-200"}
                    ${
                      !settings.is_active ? "opacity-50 cursor-not-allowed" : ""
                    }
                  `}
                >
                  <span
                    className={`
                      inline-block h-4 w-4 transform rounded-full bg-white transition-transform
                      ${passwordProtected ? "translate-x-6" : "translate-x-1"}
                    `}
                  />
                </button>
              </div>

              {passwordProtected && (
                <Input
                  type="password"
                  label="New Password"
                  placeholder={
                    settings.password_protected
                      ? "Leave blank to keep current"
                      : "Enter new password"
                  }
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  fullWidth
                  helperText={
                    settings.password_protected
                      ? "Enter a new password to change, or leave blank to keep existing"
                      : "Set a password to protect access"
                  }
                  disabled={!settings.is_active}
                />
              )}
            </div>

            {/* Expiration */}
            <div className="space-y-2">
              <label className="flex items-center gap-2 text-sm font-medium text-gray-700">
                <Calendar className="w-4 h-4" />
                Expiration
              </label>
              <Dropdown
                items={EXPIRATION_OPTIONS}
                value={expiration}
                onChange={(value) => {
                  setExpiration(value);
                  if (value === "custom") {
                    // Keep existing custom date if available
                    if (!customExpirationDate && settings.expires_at) {
                      setCustomExpirationDate(settings.expires_at);
                    }
                  } else {
                    setCustomExpirationDate(null);
                  }
                }}
                width="full"
                triggerClassName="w-full"
                disabled={!settings.is_active}
              />
              {expiration === "custom" && (
                <div className="mt-2">
                  <Input
                    type="datetime-local"
                    label="Custom Expiration Date"
                    value={
                      customExpirationDate
                        ? new Date(customExpirationDate)
                            .toISOString()
                            .slice(0, 16)
                        : ""
                    }
                    onChange={(e) => {
                      const dateValue = e.target.value;
                      if (dateValue) {
                        setCustomExpirationDate(
                          new Date(dateValue).toISOString()
                        );
                      } else {
                        setCustomExpirationDate(null);
                      }
                    }}
                    fullWidth
                    disabled={!settings.is_active}
                  />
                </div>
              )}
              {expiration !== "custom" && settings.expires_at && (
                <div className="mt-2 p-2 bg-gray-50 rounded border border-gray-200">
                  <p className="text-xs text-gray-500 mb-1">
                    Current expiration:
                  </p>
                  <p className="text-sm font-medium text-gray-900">
                    {formatDate(settings.expires_at)}
                  </p>
                </div>
              )}
            </div>

            {/* Permissions */}
            <div className="space-y-2">
              <label className="flex items-center gap-2 text-sm font-medium text-gray-700">
                <Eye className="w-4 h-4" />
                Access Level
              </label>
              <Dropdown
                items={PERMISSION_OPTIONS}
                value={permissions}
                onChange={(value) =>
                  setPermissions(value as "view" | "download")
                }
                width="full"
                triggerClassName="w-full"
                disabled={!settings.is_active}
              />
            </div>
          </div>
        </CardContent>

        <CardFooter>
          <div className="flex items-center justify-between w-full gap-3">
            <Button
              variant="danger"
              onClick={() => setShowRevokeConfirm(true)}
              leftIcon={<Trash2 className="w-4 h-4" />}
              disabled={!settings.is_active}
            >
              Revoke Share
            </Button>

            <Button
              variant="primary"
              onClick={handleSaveSettings}
              isLoading={isSaving}
              leftIcon={<Save className="w-4 h-4" />}
              disabled={!hasChanges || !settings.is_active}
            >
              Save Changes
            </Button>
          </div>
        </CardFooter>
      </Card>

      {/* Revoke Confirmation Modal */}
      <Modal
        isOpen={showRevokeConfirm}
        onClose={() => setShowRevokeConfirm(false)}
        title="Revoke Share Link"
        size="sm"
        footer={
          <>
            <Button variant="ghost" onClick={() => setShowRevokeConfirm(false)}>
              Cancel
            </Button>
            <Button
              variant="danger"
              onClick={handleRevoke}
              isLoading={isRevoking}
            >
              Revoke
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          <Alert
            variant="warning"
            showIcon
            description="This action cannot be undone. The share link will become permanently inaccessible."
          />
          <p className="text-sm text-gray-700">
            Are you sure you want to revoke this share? Anyone with the link
            will no longer be able to access the report.
          </p>
        </div>
      </Modal>
    </>
  );
};
export default ShareSettings;
