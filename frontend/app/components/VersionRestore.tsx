"use client";

import React, { useState } from 'react';
import { Modal } from './Modal';
import { Button } from './Button';
import { Alert } from './Alert';
import { Spinner } from './Spinner';
import { Badge } from './Badge';

export interface Version {
  id: string;
  version_number: number;
  created_at: string;
  created_by: string;
  change_summary: string;
}

export interface VersionRestoreProps {
  reportId: string;
  version: Version;
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (versionId: string) => Promise<void>;
}

const VersionRestore: React.FC<VersionRestoreProps> = ({
  reportId,
  version,
  isOpen,
  onClose,
  onConfirm
}) => {
  const [confirmed, setConfirmed] = useState(false);
  const [restoring, setRestoring] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleRestore = async () => {
    if (!confirmed) {
      setError('Please confirm by checking the checkbox');
      return;
    }

    try {
      setRestoring(true);
      setError(null);

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/versions/${reportId}/${version.id}/restore`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          }
        }
      );

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || `Failed to restore version: ${response.statusText}`);
      }

      await onConfirm(version.id);
      setSuccess(true);

      // Auto-close after success
      setTimeout(() => {
        handleClose();
      }, 1500);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to restore version');
    } finally {
      setRestoring(false);
    }
  };

  const handleClose = () => {
    setConfirmed(false);
    setError(null);
    setSuccess(false);
    onClose();
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={!restoring ? handleClose : undefined}
      title="Restore Previous Version"
      size="md"
    >
      <div className="space-y-6">
        {/* Warning Alert */}
        <Alert variant="warning">
          <strong>Important:</strong> Restoring this version will create a new version based on the
          selected version. Your current version will remain in the version history and can be
          restored later if needed.
        </Alert>

        {/* Version Details */}
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-lg font-semibold text-gray-900">
              Version {version.version_number}
            </h3>
            <Badge variant="primary">Selected</Badge>
          </div>

          <div className="space-y-2">
            <div>
              <span className="text-sm font-medium text-gray-700">Change Summary:</span>
              <p className="text-sm text-gray-600 mt-1">{version.change_summary}</p>
            </div>

            <div className="grid grid-cols-2 gap-4 pt-2 border-t border-gray-200">
              <div>
                <span className="text-xs font-medium text-gray-500">Created By:</span>
                <p className="text-sm text-gray-900">{version.created_by}</p>
              </div>
              <div>
                <span className="text-xs font-medium text-gray-500">Date:</span>
                <p className="text-sm text-gray-900">{formatDate(version.created_at)}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Success Message */}
        {success && (
          <Alert variant="success">
            Version {version.version_number} has been successfully restored!
          </Alert>
        )}

        {/* Error Message */}
        {error && (
          <Alert variant="error" onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {/* Confirmation Checkbox */}
        {!success && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <label className="flex items-start gap-3 cursor-pointer group">
              <input
                type="checkbox"
                checked={confirmed}
                onChange={(e) => setConfirmed(e.target.checked)}
                disabled={restoring}
                className="mt-1 h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
                aria-describedby="restore-confirmation-text"
              />
              <span
                id="restore-confirmation-text"
                className="text-sm text-gray-700 group-hover:text-gray-900"
              >
                I understand that restoring this version will create a new version, and my current
                version will be preserved in the version history.
              </span>
            </label>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-3 justify-end pt-4 border-t border-gray-200">
          <Button
            variant="secondary"
            onClick={handleClose}
            disabled={restoring}
          >
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={handleRestore}
            disabled={!confirmed || restoring || success}
            aria-label={`Restore version ${version.version_number}`}
          >
            {restoring ? (
              <>
                <Spinner size="sm" className="mr-2" />
                Restoring...
              </>
            ) : success ? (
              'Restored!'
            ) : (
              'Restore Version'
            )}
          </Button>
        </div>

        {/* Screen Reader Announcements */}
        <div className="sr-only" role="status" aria-live="polite" aria-atomic="true">
          {restoring && 'Restoring version, please wait'}
          {success && 'Version restored successfully'}
          {error && `Error: ${error}`}
        </div>
      </div>
    </Modal>
  );
};

export { VersionRestore };
