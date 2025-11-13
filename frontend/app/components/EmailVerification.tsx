"use client";

import React, { useState, useEffect } from "react";
import { Input } from "./Input";
import { Button } from "./Button";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "./Card";
import { Alert } from "./Alert";
import { Mail, CheckCircle } from "lucide-react";

export interface EmailVerificationProps {
  /** Email address to verify */
  email?: string;
  /** Callback when verification is successful */
  onSuccess?: () => void;
  /** Custom API URL */
  apiUrl?: string;
}

export const EmailVerification: React.FC<EmailVerificationProps> = ({
  email,
  onSuccess,
  apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080",
}) => {
  const [code, setCode] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isResending, setIsResending] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [resendCountdown, setResendCountdown] = useState(0);

  useEffect(() => {
    let timer: NodeJS.Timeout;
    if (resendCountdown > 0) {
      timer = setTimeout(() => setResendCountdown(resendCountdown - 1), 1000);
    }
    return () => clearTimeout(timer);
  }, [resendCountdown]);

  const validateCode = (value: string): boolean => {
    return /^\d{6}$/.test(value);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage("");
    setSuccessMessage("");

    if (!validateCode(code)) {
      setErrorMessage("Please enter a valid 6-digit verification code");
      return;
    }

    if (!email) {
      setErrorMessage("Email address is required");
      return;
    }

    setIsLoading(true);
    const abortController = new AbortController();
    const timeoutId = setTimeout(() => abortController.abort(), 10000); // 10 second timeout

    try {
      const response = await fetch(`${apiUrl}/users/verify-email`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          code,
        }),
        signal: abortController.signal,
      });

      if (!response.ok) {
        let errorMessage = "Verification failed";
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorMessage;
        } catch {
          const errorText = await response.text().catch(() => "");
          errorMessage =
            errorText || `Verification failed: ${response.statusText}`;
        }
        throw new Error(errorMessage);
      }

      await response.json();
      setSuccessMessage("Email verified successfully! Redirecting...");
      setTimeout(() => {
        onSuccess?.();
      }, 2000);
    } catch (error) {
      if (error instanceof Error && error.name === "AbortError") {
        setErrorMessage("Request timed out. Please try again.");
      } else {
        setErrorMessage(
          error instanceof Error
            ? error.message
            : "Verification failed. Please try again."
        );
      }
    } finally {
      clearTimeout(timeoutId);
      setIsLoading(false);
    }
  };

  const handleResendCode = async () => {
    if (resendCountdown > 0) return;

    if (!email) {
      setErrorMessage("Email address is required");
      return;
    }

    setErrorMessage("");
    setSuccessMessage("");
    setIsResending(true);
    const abortController = new AbortController();
    const timeoutId = setTimeout(() => abortController.abort(), 10000); // 10 second timeout

    try {
      const response = await fetch(`${apiUrl}/users/resend-verification`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email }),
        signal: abortController.signal,
      });

      if (!response.ok) {
        let errorMessage = "Failed to resend code";
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorMessage;
        } catch {
          const errorText = await response.text().catch(() => "");
          errorMessage =
            errorText || `Failed to resend code: ${response.statusText}`;
        }
        throw new Error(errorMessage);
      }

      await response.json();
      setSuccessMessage("Verification code sent! Please check your email.");
      setResendCountdown(60);
    } catch (error) {
      if (error instanceof Error && error.name === "AbortError") {
        setErrorMessage("Request timed out. Please try again.");
      } else {
        setErrorMessage(
          error instanceof Error
            ? error.message
            : "Failed to resend code. Please try again."
        );
      }
    } finally {
      clearTimeout(timeoutId);
      setIsResending(false);
    }
  };

  const handleCodeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.replace(/\D/g, "").slice(0, 6);
    setCode(value);
  };

  return (
    <Card className="max-w-md mx-auto">
      <CardHeader>
        <CardTitle>Verify Your Email</CardTitle>
        <CardDescription>
          {email ? (
            <>
              We sent a verification code to <strong>{email}</strong>
            </>
          ) : (
            "Please enter the verification code sent to your email"
          )}
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
            title="Verification Failed"
            description={errorMessage}
            dismissible
            onClose={() => setErrorMessage("")}
            className="mb-4"
          />
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <Input
              label="Verification Code"
              leftIcon={<Mail className="w-5 h-5" />}
              value={code}
              onChange={handleCodeChange}
              placeholder="000000"
              maxLength={6}
              required
              fullWidth
              disabled={isLoading}
              className="text-center text-2xl tracking-widest font-mono"
              helperText="Enter the 6-digit code from your email"
            />
          </div>

          <Button
            type="submit"
            fullWidth
            isLoading={isLoading}
            disabled={isLoading || !validateCode(code)}
            leftIcon={<CheckCircle className="w-5 h-5" />}
          >
            Verify Email
          </Button>

          <div className="text-center">
            <p className="text-sm text-gray-600 mb-2">
              Didn't receive the code?
            </p>
            <Button
              type="button"
              variant="ghost"
              onClick={handleResendCode}
              disabled={resendCountdown > 0 || isResending}
              isLoading={isResending}
            >
              {resendCountdown > 0
                ? `Resend code in ${resendCountdown}s`
                : "Resend Code"}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
};
