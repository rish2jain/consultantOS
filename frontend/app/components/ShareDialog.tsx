"use client";

import React, { useState } from 'react';
import { Modal } from './Modal';
import { Button } from './Button';
import { Input } from './Input';
import { Dropdown, DropdownItem } from './Dropdown';
import { Alert } from './Alert';
import { Spinner } from './Spinner';
import { Copy, Check, Link, Lock, Calendar, Eye } from 'lucide-react';

export interface ShareDialogProps {
  /** Report ID to share */
  reportId: string;
  /** Whether dialog is open */
  isOpen: boolean;
  /** Close handler */
  onClose: () => void;
  /** Success callback with share link */
  onSuccess?: (shareLink: string, shareId: string) => void;
}

interface ShareSettings {
  password: string;
  expiresAt: string;
  permissions: 'view' | 'download';
}

const EXPIRATION_OPTIONS: DropdownItem[] = [
  { label: '24 hours', value: '24h' },
  { label: '7 days', value: '7d' },
  { label: '30 days', value: '30d' },
  { label: 'Never', value: 'never' },
];

const PERMISSION_OPTIONS: DropdownItem[] = [
  { label: 'View only', value: 'view', icon: <Eye className="w-4 h-4" /> },
  { label: 'View & Download', value: 'download', icon: <Eye className="w-4 h-4" /> },
];

export const ShareDialog: React.FC<ShareDialogProps> = ({
  reportId,
  isOpen,
  onClose,
  onSuccess,
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [shareLink, setShareLink] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const [passwordProtected, setPasswordProtected] = useState(false);
  const [password, setPassword] = useState('');
  const [expiration, setExpiration] = useState<string>('7d');
  const [permissions, setPermissions] = useState<'view' | 'download'>('view');

  const calculateExpirationDate = (option: string): string | undefined => {
    if (option === 'never') return undefined;

    const now = new Date();
    if (option === '24h') {
      now.setHours(now.getHours() + 24);
    } else if (option === '7d') {
      now.setDate(now.getDate() + 7);
    } else if (option === '30d') {
      now.setDate(now.getDate() + 30);
    }

    return now.toISOString();
  };

  const handleCreateShare = async () => {
    setError(null);
    setIsLoading(true);

    try {
      const response = await fetch('/api/shares', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          report_id: reportId,
          password: passwordProtected ? password : undefined,
          expires_at: calculateExpirationDate(expiration),
          permissions,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create share link');
      }

      const data = await response.json();
      const link = `${window.location.origin}/shared/${data.share_id}`;

      setShareLink(link);
      onSuccess?.(link, data.share_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopyLink = async () => {
    if (!shareLink) return;

    try {
      await navigator.clipboard.writeText(shareLink);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      setError('Failed to copy link to clipboard');
    }
  };

  const handleClose = () => {
    setShareLink(null);
    setPassword('');
    setPasswordProtected(false);
    setExpiration('7d');
    setPermissions('view');
    setError(null);
    setCopied(false);
    onClose();
  };

  const footer = shareLink ? (
    <Button onClick={handleClose} variant="primary">
      Done
    </Button>
  ) : (
    <>
      <Button onClick={handleClose} variant="ghost">
        Cancel
      </Button>
      <Button
        onClick={handleCreateShare}
        variant="primary"
        isLoading={isLoading}
        disabled={passwordProtected && !password.trim()}
      >
        Create Share Link
      </Button>
    </>
  );

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Share Report"
      description="Create a shareable link for this report"
      size="md"
      footer={footer}
    >
      <div className="space-y-6">
        {error && (
          <Alert
            variant="error"
            title="Error"
            description={error}
            dismissible
            onClose={() => setError(null)}
          />
        )}

        {shareLink ? (
          // Share link created - show copy interface
          <div className="space-y-4">
            <Alert
              variant="success"
              title="Share link created"
              description="Your report is ready to share!"
              showIcon
            />

            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">
                Share Link
              </label>
              <div className="flex gap-2">
                <Input
                  value={shareLink}
                  readOnly
                  fullWidth
                  leftIcon={<Link className="w-4 h-4" />}
                  className="font-mono text-sm"
                  aria-label="Share link"
                />
                <Button
                  onClick={handleCopyLink}
                  variant={copied ? 'success' : 'outline'}
                  leftIcon={copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                  aria-label={copied ? 'Link copied' : 'Copy link'}
                >
                  {copied ? 'Copied!' : 'Copy'}
                </Button>
              </div>
            </div>

            <div className="bg-gray-50 rounded-lg p-4 space-y-2">
              <h4 className="text-sm font-semibold text-gray-900">Share Settings</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li className="flex items-center gap-2">
                  <Lock className="w-4 h-4" />
                  {passwordProtected ? 'Password protected' : 'No password required'}
                </li>
                <li className="flex items-center gap-2">
                  <Calendar className="w-4 h-4" />
                  Expires: {EXPIRATION_OPTIONS.find(opt => opt.value === expiration)?.label}
                </li>
                <li className="flex items-center gap-2">
                  <Eye className="w-4 h-4" />
                  Access: {PERMISSION_OPTIONS.find(opt => opt.value === permissions)?.label}
                </li>
              </ul>
            </div>
          </div>
        ) : (
          // Configuration interface
          <div className="space-y-6">
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
                  className={`
                    relative inline-flex h-6 w-11 items-center rounded-full transition-colors
                    focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
                    ${passwordProtected ? 'bg-primary-600' : 'bg-gray-200'}
                  `}
                >
                  <span
                    className={`
                      inline-block h-4 w-4 transform rounded-full bg-white transition-transform
                      ${passwordProtected ? 'translate-x-6' : 'translate-x-1'}
                    `}
                  />
                </button>
              </div>

              {passwordProtected && (
                <Input
                  type="password"
                  label="Password"
                  placeholder="Enter password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  fullWidth
                  required
                  helperText="Recipients will need this password to access the report"
                  leftIcon={<Lock className="w-4 h-4" />}
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
                onChange={(value) => setExpiration(value)}
                width="full"
                triggerClassName="w-full"
              />
              <p className="text-xs text-gray-500">
                Link will expire and become inaccessible
              </p>
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
                onChange={(value) => setPermissions(value as 'view' | 'download')}
                width="full"
                triggerClassName="w-full"
              />
              <p className="text-xs text-gray-500">
                {permissions === 'view'
                  ? 'Recipients can view the report online only'
                  : 'Recipients can view and download the report PDF'}
              </p>
            </div>
          </div>
        )}

        {isLoading && (
          <div className="flex items-center justify-center py-8">
            <Spinner size="lg" label="Creating share link..." />
          </div>
        )}
      </div>
    </Modal>
  );
};
