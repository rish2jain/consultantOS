"use client";

import React, { useState } from 'react';
import { Input } from './Input';
import { Button } from './Button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from './Card';
import { Alert } from './Alert';
import { Mail, ArrowLeft } from 'lucide-react';

export interface PasswordResetFormProps {
  /** Callback when reset request is successful */
  onSuccess?: (email: string) => void;
  /** Custom API URL */
  apiUrl?: string;
}

const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const PasswordResetForm: React.FC<PasswordResetFormProps> = ({
  onSuccess,
  apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080',
}) => {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [emailError, setEmailError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage('');
    setSuccessMessage('');
    setEmailError('');

    if (!email) {
      setEmailError('Email is required');
      return;
    }

    if (!validateEmail(email)) {
      setEmailError('Please enter a valid email address');
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch(`${apiUrl}/users/request-password-reset`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to send reset email');
      }

      setSuccessMessage('Password reset instructions sent! Please check your email.');
      onSuccess?.(email);
      setEmail('');
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : 'Failed to send reset email. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEmail(e.target.value);
    if (emailError) {
      setEmailError('');
    }
  };

  return (
    <Card className="max-w-md mx-auto">
      <CardHeader>
        <CardTitle>Reset Password</CardTitle>
        <CardDescription>
          Enter your email address and we'll send you instructions to reset your password
        </CardDescription>
      </CardHeader>

      <CardContent>
        {successMessage && (
          <Alert
            variant="success"
            title="Check Your Email"
            description={successMessage}
            showIcon
            className="mb-4"
          />
        )}

        {errorMessage && (
          <Alert
            variant="error"
            title="Request Failed"
            description={errorMessage}
            dismissible
            onClose={() => setErrorMessage('')}
            className="mb-4"
          />
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <Input
            label="Email Address"
            type="email"
            leftIcon={<Mail className="w-5 h-5" />}
            value={email}
            onChange={handleEmailChange}
            error={emailError}
            placeholder="you@example.com"
            required
            fullWidth
            disabled={isLoading}
          />

          <Button
            type="submit"
            fullWidth
            isLoading={isLoading}
            disabled={isLoading}
          >
            Send Reset Instructions
          </Button>

          <div className="text-center">
            <a
              href="/login"
              className="inline-flex items-center gap-2 text-sm text-primary-600 hover:underline"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Sign In
            </a>
          </div>
        </form>
      </CardContent>
    </Card>
  );
};
