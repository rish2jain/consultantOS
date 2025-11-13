"use client";

import React, { useState, useEffect } from 'react';
import { Input } from './Input';
import { Button } from './Button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from './Card';
import { Alert } from './Alert';
import { Modal } from './Modal';
import { User, Mail, Lock, Save, Trash2 } from 'lucide-react';

export interface ProfileSettingsProps {
  /** User API key for authentication */
  apiKey?: string;
  /** Callback when profile is updated */
  onProfileUpdate?: () => void;
  /** Callback when account is deleted */
  onAccountDelete?: () => void;
  /** Custom API URL */
  apiUrl?: string;
}

interface UserProfile {
  email: string;
  name: string;
  created_at?: string;
}

interface ChangePasswordData {
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
}

interface PasswordErrors {
  currentPassword?: string;
  newPassword?: string;
  confirmPassword?: string;
}

const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

const getPasswordStrength = (password: string): { score: number; label: string; color: string } => {
  let score = 0;

  if (password.length >= 8) score++;
  if (password.length >= 12) score++;
  if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score++;
  if (/\d/.test(password)) score++;
  if (/[^A-Za-z0-9]/.test(password)) score++;

  if (score <= 2) return { score, label: 'Weak', color: 'bg-red-500' };
  if (score === 3) return { score, label: 'Fair', color: 'bg-yellow-500' };
  if (score === 4) return { score, label: 'Good', color: 'bg-blue-500' };
  return { score, label: 'Strong', color: 'bg-green-500' };
};

export const ProfileSettings: React.FC<ProfileSettingsProps> = ({
  apiKey,
  onProfileUpdate,
  onAccountDelete,
  apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080',
}) => {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isLoadingProfile, setIsLoadingProfile] = useState(true);
  const [isUpdatingProfile, setIsUpdatingProfile] = useState(false);
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [isDeletingAccount, setIsDeletingAccount] = useState(false);

  const [editedProfile, setEditedProfile] = useState({ name: '', email: '' });
  const [profileErrors, setProfileErrors] = useState({ name: '', email: '' });

  const [passwordData, setPasswordData] = useState<ChangePasswordData>({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });
  const [passwordErrors, setPasswordErrors] = useState<PasswordErrors>({});

  const [successMessage, setSuccessMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');

  const passwordStrength = getPasswordStrength(passwordData.newPassword);

  const fetchProfile = React.useCallback(async () => {
    if (!apiKey) {
      setErrorMessage('API key required to view profile');
      setIsLoadingProfile(false);
      return;
    }

    try {
      const response = await fetch(`${apiUrl}/users/profile`, {
        headers: {
          'X-API-Key': apiKey,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch profile');
      }

      const data = await response.json();
      setProfile(data);
      setEditedProfile({ name: data.name, email: data.email });
    } catch (error) {
      setErrorMessage('Failed to load profile');
    } finally {
      setIsLoadingProfile(false);
    }
  }, [apiKey, apiUrl]);

  useEffect(() => {
    fetchProfile();
  }, [fetchProfile]);

  const validateProfileForm = (): boolean => {
    const errors = { name: '', email: '' };

    if (!editedProfile.name.trim()) {
      errors.name = 'Name is required';
    }

    if (!editedProfile.email) {
      errors.email = 'Email is required';
    } else if (!validateEmail(editedProfile.email)) {
      errors.email = 'Invalid email address';
    }

    setProfileErrors(errors);
    return !errors.name && !errors.email;
  };

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setSuccessMessage('');
    setErrorMessage('');

    if (!validateProfileForm()) return;

    setIsUpdatingProfile(true);

    try {
      const response = await fetch(`${apiUrl}/users/profile`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': apiKey || '',
        },
        body: JSON.stringify(editedProfile),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to update profile');
      }

      const data = await response.json();
      setProfile(data);
      setSuccessMessage('Profile updated successfully');
      onProfileUpdate?.();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : 'Failed to update profile');
    } finally {
      setIsUpdatingProfile(false);
    }
  };

  const validatePasswordForm = (): boolean => {
    const errors: PasswordErrors = {};

    if (!passwordData.currentPassword) {
      errors.currentPassword = 'Current password is required';
    }

    if (!passwordData.newPassword) {
      errors.newPassword = 'New password is required';
    } else if (passwordData.newPassword.length < 8) {
      errors.newPassword = 'Password must be at least 8 characters';
    } else if (passwordStrength.score < 3) {
      errors.newPassword = 'Password is too weak';
    }

    if (!passwordData.confirmPassword) {
      errors.confirmPassword = 'Please confirm your password';
    } else if (passwordData.newPassword !== passwordData.confirmPassword) {
      errors.confirmPassword = 'Passwords do not match';
    }

    setPasswordErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setSuccessMessage('');
    setErrorMessage('');

    if (!validatePasswordForm()) return;

    setIsChangingPassword(true);

    try {
      const response = await fetch(`${apiUrl}/users/change-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': apiKey || '',
        },
        body: JSON.stringify({
          current_password: passwordData.currentPassword,
          new_password: passwordData.newPassword,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to change password');
      }

      setSuccessMessage('Password changed successfully');
      setPasswordData({ currentPassword: '', newPassword: '', confirmPassword: '' });
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : 'Failed to change password');
    } finally {
      setIsChangingPassword(false);
    }
  };

  const handleDeleteAccount = async () => {
    setIsDeletingAccount(true);

    try {
      const response = await fetch(`${apiUrl}/users/profile`, {
        method: 'DELETE',
        headers: {
          'X-API-Key': apiKey || '',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to delete account');
      }

      setSuccessMessage('Account deleted successfully');
      setTimeout(() => {
        onAccountDelete?.();
      }, 2000);
    } catch (error) {
      setErrorMessage('Failed to delete account');
    } finally {
      setIsDeletingAccount(false);
      setShowDeleteModal(false);
    }
  };

  if (isLoadingProfile) {
    return (
      <Card className="max-w-2xl mx-auto">
        <CardContent className="py-12 text-center text-gray-500">
          Loading profile...
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {successMessage && (
        <Alert
          variant="success"
          title="Success"
          description={successMessage}
          dismissible
          onClose={() => setSuccessMessage('')}
        />
      )}

      {errorMessage && (
        <Alert
          variant="error"
          title="Error"
          description={errorMessage}
          dismissible
          onClose={() => setErrorMessage('')}
        />
      )}

      {/* Profile Information */}
      <Card>
        <CardHeader>
          <CardTitle>Profile Information</CardTitle>
          <CardDescription>Update your account details</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleUpdateProfile} className="space-y-4">
            <Input
              label="Full Name"
              leftIcon={<User className="w-5 h-5" />}
              value={editedProfile.name}
              onChange={(e) => {
                setEditedProfile({ ...editedProfile, name: e.target.value });
                setProfileErrors({ ...profileErrors, name: '' });
              }}
              error={profileErrors.name}
              required
              fullWidth
              disabled={isUpdatingProfile}
            />

            <Input
              label="Email Address"
              type="email"
              leftIcon={<Mail className="w-5 h-5" />}
              value={editedProfile.email}
              onChange={(e) => {
                setEditedProfile({ ...editedProfile, email: e.target.value });
                setProfileErrors({ ...profileErrors, email: '' });
              }}
              error={profileErrors.email}
              required
              fullWidth
              disabled={isUpdatingProfile}
            />

            {profile?.created_at && (
              <div className="text-sm text-gray-500">
                Member since {new Date(profile.created_at).toLocaleDateString()}
              </div>
            )}

            <Button
              type="submit"
              leftIcon={<Save className="w-5 h-5" />}
              isLoading={isUpdatingProfile}
              disabled={isUpdatingProfile}
            >
              Save Changes
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Change Password */}
      <Card>
        <CardHeader>
          <CardTitle>Change Password</CardTitle>
          <CardDescription>Update your password to keep your account secure</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleChangePassword} className="space-y-4">
            <Input
              label="Current Password"
              type="password"
              leftIcon={<Lock className="w-5 h-5" />}
              value={passwordData.currentPassword}
              onChange={(e) => {
                setPasswordData({ ...passwordData, currentPassword: e.target.value });
                setPasswordErrors({ ...passwordErrors, currentPassword: undefined });
              }}
              error={passwordErrors.currentPassword}
              required
              fullWidth
              disabled={isChangingPassword}
            />

            <div>
              <Input
                label="New Password"
                type="password"
                leftIcon={<Lock className="w-5 h-5" />}
                value={passwordData.newPassword}
                onChange={(e) => {
                  setPasswordData({ ...passwordData, newPassword: e.target.value });
                  setPasswordErrors({ ...passwordErrors, newPassword: undefined });
                }}
                error={passwordErrors.newPassword}
                required
                fullWidth
                disabled={isChangingPassword}
              />

              {passwordData.newPassword && (
                <div className="mt-2">
                  <div className="flex items-center justify-between text-xs mb-1">
                    <span className="text-gray-600">Password strength:</span>
                    <span className={`font-medium ${
                      passwordStrength.score <= 2 ? 'text-red-600' :
                      passwordStrength.score === 3 ? 'text-yellow-600' :
                      passwordStrength.score === 4 ? 'text-blue-600' :
                      'text-green-600'
                    }`}>
                      {passwordStrength.label}
                    </span>
                  </div>
                  <div className="w-full h-1.5 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className={`h-full transition-all duration-300 ${passwordStrength.color}`}
                      style={{ width: `${(passwordStrength.score / 5) * 100}%` }}
                    />
                  </div>
                </div>
              )}
            </div>

            <Input
              label="Confirm New Password"
              type="password"
              leftIcon={<Lock className="w-5 h-5" />}
              value={passwordData.confirmPassword}
              onChange={(e) => {
                setPasswordData({ ...passwordData, confirmPassword: e.target.value });
                setPasswordErrors({ ...passwordErrors, confirmPassword: undefined });
              }}
              error={passwordErrors.confirmPassword}
              required
              fullWidth
              disabled={isChangingPassword}
            />

            <Button
              type="submit"
              isLoading={isChangingPassword}
              disabled={isChangingPassword}
            >
              Change Password
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Danger Zone */}
      <Card variant="outlined" className="border-red-200">
        <CardHeader>
          <CardTitle className="text-red-600">Danger Zone</CardTitle>
          <CardDescription>Irreversible account actions</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-start justify-between gap-4">
            <div>
              <h4 className="font-medium text-gray-900">Delete Account</h4>
              <p className="text-sm text-gray-600 mt-1">
                Permanently delete your account and all associated data. This action cannot be undone.
              </p>
            </div>
            <Button
              variant="danger"
              leftIcon={<Trash2 className="w-5 h-5" />}
              onClick={() => setShowDeleteModal(true)}
            >
              Delete Account
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={showDeleteModal}
        onClose={() => !isDeletingAccount && setShowDeleteModal(false)}
        title="Delete Account"
      >
        <div className="space-y-4">
          <Alert
            variant="warning"
            title="Warning"
            description="This action cannot be undone. All your data will be permanently deleted."
          />

          <p className="text-sm text-gray-700">
            Are you sure you want to delete your account? This will permanently remove:
          </p>

          <ul className="text-sm text-gray-700 list-disc list-inside space-y-1">
            <li>Your profile and account information</li>
            <li>All saved analyses and reports</li>
            <li>Shared content and collaborations</li>
            <li>Custom templates and settings</li>
          </ul>

          <div className="flex gap-3 justify-end pt-4">
            <Button
              variant="outline"
              onClick={() => setShowDeleteModal(false)}
              disabled={isDeletingAccount}
            >
              Cancel
            </Button>
            <Button
              variant="danger"
              onClick={handleDeleteAccount}
              isLoading={isDeletingAccount}
              disabled={isDeletingAccount}
            >
              Yes, Delete My Account
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};
export default ProfileSettings;
