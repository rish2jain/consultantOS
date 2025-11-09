"use client";

import React, { useState, useEffect } from 'react';
import { Input } from './Input';
import { Button } from './Button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from './Card';
import { Alert } from './Alert';
import { Lock, CheckCircle } from 'lucide-react';

export interface PasswordResetConfirmProps {
  /** Reset token from URL or email */
  token?: string;
  /** Callback when password reset is successful */
  onSuccess?: () => void;
  /** Custom API URL */
  apiUrl?: string;
}

interface FormData {
  password: string;
  confirmPassword: string;
}

interface FormErrors {
  password?: string;
  confirmPassword?: string;
}

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

export const PasswordResetConfirm: React.FC<PasswordResetConfirmProps> = ({
  token,
  onSuccess,
  apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080',
}) => {
  const [formData, setFormData] = useState<FormData>({
    password: '',
    confirmPassword: '',
  });

  const [errors, setErrors] = useState<FormErrors>({});
  const [isLoading, setIsLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [tokenValid, setTokenValid] = useState(true);

  const passwordStrength = getPasswordStrength(formData.password);

  useEffect(() => {
    // Validate token on mount
    if (!token) {
      setTokenValid(false);
      setErrorMessage('Invalid or missing reset token');
    }
  }, [token]);

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    } else if (passwordStrength.score < 3) {
      newErrors.password = 'Password is too weak. Please use a stronger password';
    }

    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage('');
    setSuccessMessage('');

    if (!tokenValid) {
      setErrorMessage('Invalid reset token. Please request a new password reset.');
      return;
    }

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch(`${apiUrl}/users/reset-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token,
          new_password: formData.password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Password reset failed');
      }

      setSuccessMessage('Password reset successful! Redirecting to login...');
      setTimeout(() => {
        onSuccess?.();
      }, 2000);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : 'Password reset failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (field: keyof FormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  if (!tokenValid) {
    return (
      <Card className="max-w-md mx-auto">
        <CardHeader>
          <CardTitle>Invalid Reset Link</CardTitle>
          <CardDescription>
            This password reset link is invalid or has expired
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Alert
            variant="error"
            title="Invalid Token"
            description="Please request a new password reset link."
            className="mb-4"
          />
          <Button
            fullWidth
            onClick={() => window.location.href = '/password-reset'}
          >
            Request New Reset Link
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="max-w-md mx-auto">
      <CardHeader>
        <CardTitle>Set New Password</CardTitle>
        <CardDescription>
          Choose a strong password for your account
        </CardDescription>
      </CardHeader>

      <CardContent>
        {successMessage && (
          <Alert
            variant="success"
            title="Success!"
            description={successMessage}
            showIcon
            className="mb-4"
          />
        )}

        {errorMessage && (
          <Alert
            variant="error"
            title="Reset Failed"
            description={errorMessage}
            dismissible
            onClose={() => setErrorMessage('')}
            className="mb-4"
          />
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Input
              label="New Password"
              type="password"
              leftIcon={<Lock className="w-5 h-5" />}
              value={formData.password}
              onChange={(e) => handleChange('password', e.target.value)}
              error={errors.password}
              placeholder="Min. 8 characters"
              required
              fullWidth
              disabled={isLoading}
            />

            {formData.password && (
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
                <ul className="mt-2 text-xs text-gray-600 space-y-1">
                  <li className={formData.password.length >= 8 ? 'text-green-600' : ''}>
                    {formData.password.length >= 8 ? '✓' : '○'} At least 8 characters
                  </li>
                  <li className={/[A-Z]/.test(formData.password) && /[a-z]/.test(formData.password) ? 'text-green-600' : ''}>
                    {/[A-Z]/.test(formData.password) && /[a-z]/.test(formData.password) ? '✓' : '○'} Upper and lowercase letters
                  </li>
                  <li className={/\d/.test(formData.password) ? 'text-green-600' : ''}>
                    {/\d/.test(formData.password) ? '✓' : '○'} At least one number
                  </li>
                  <li className={/[^A-Za-z0-9]/.test(formData.password) ? 'text-green-600' : ''}>
                    {/[^A-Za-z0-9]/.test(formData.password) ? '✓' : '○'} Special character
                  </li>
                </ul>
              </div>
            )}
          </div>

          <Input
            label="Confirm New Password"
            type="password"
            leftIcon={<Lock className="w-5 h-5" />}
            value={formData.confirmPassword}
            onChange={(e) => handleChange('confirmPassword', e.target.value)}
            error={errors.confirmPassword}
            placeholder="Re-enter password"
            required
            fullWidth
            disabled={isLoading}
          />

          <Button
            type="submit"
            fullWidth
            isLoading={isLoading}
            disabled={isLoading}
            leftIcon={<CheckCircle className="w-5 h-5" />}
          >
            Reset Password
          </Button>

          <p className="text-sm text-center text-gray-600">
            Remember your password?{' '}
            <a href="/login" className="text-primary-600 hover:underline font-medium">
              Sign in
            </a>
          </p>
        </form>
      </CardContent>
    </Card>
  );
};
