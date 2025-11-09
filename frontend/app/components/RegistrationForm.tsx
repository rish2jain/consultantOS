"use client";

import React, { useState } from "react";
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
import { Mail, User, Lock, CheckCircle } from "lucide-react";

export interface RegistrationFormProps {
  /** Callback when registration is successful */
  onSuccess?: (email: string) => void;
  /** Custom API URL */
  apiUrl?: string;
}

interface FormData {
  email: string;
  password: string;
  confirmPassword: string;
  name: string;
  termsAccepted: boolean;
}

interface FormErrors {
  email?: string;
  password?: string;
  confirmPassword?: string;
  name?: string;
  termsAccepted?: string;
}

const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

const getPasswordStrength = (
  password: string
): { score: number; label: string; color: string } => {
  let score = 0;

  if (password.length >= 8) score++;
  if (password.length >= 12) score++;
  if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score++;
  if (/\d/.test(password)) score++;
  if (/[^A-Za-z0-9]/.test(password)) score++;

  if (score <= 2) return { score, label: "Weak", color: "bg-red-500" };
  if (score === 3) return { score, label: "Fair", color: "bg-yellow-500" };
  if (score === 4) return { score, label: "Good", color: "bg-blue-500" };
  return { score, label: "Strong", color: "bg-green-500" };
};

export const RegistrationForm: React.FC<RegistrationFormProps> = ({
  onSuccess,
  apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080",
}) => {
  const [formData, setFormData] = useState<FormData>({
    email: "",
    password: "",
    confirmPassword: "",
    name: "",
    termsAccepted: false,
  });

  const [errors, setErrors] = useState<FormErrors>({});
  const [isLoading, setIsLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  const passwordStrength = getPasswordStrength(formData.password);

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    if (!formData.name.trim()) {
      newErrors.name = "Name is required";
    }

    if (!formData.email) {
      newErrors.email = "Email is required";
    } else if (!validateEmail(formData.email)) {
      newErrors.email = "Please enter a valid email address";
    }

    if (!formData.password) {
      newErrors.password = "Password is required";
    } else if (formData.password.length < 8) {
      newErrors.password = "Password must be at least 8 characters";
    }

    if (!formData.confirmPassword) {
      newErrors.confirmPassword = "Please confirm your password";
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = "Passwords do not match";
    }

    if (!formData.termsAccepted) {
      newErrors.termsAccepted = "You must accept the terms and conditions";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage("");
    setSuccessMessage("");

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch(`${apiUrl}/users/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password,
          name: formData.name,
        }),
      });

      if (!response.ok) {
        let errorMessage = "Registration failed";
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorMessage;
        } catch {
          const errorText = await response.text().catch(() => "");
          errorMessage =
            errorText || `Registration failed: ${response.statusText}`;
        }
        throw new Error(errorMessage);
      }

      const data = await response.json();

      setSuccessMessage(
        "Registration successful! Please check your email to verify your account."
      );
      onSuccess?.(formData.email);

      // Reset form
      setFormData({
        email: "",
        password: "",
        confirmPassword: "",
        name: "",
        termsAccepted: false,
      });
    } catch (error) {
      setErrorMessage(
        error instanceof Error
          ? error.message
          : "Registration failed. Please try again."
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (field: keyof FormData, value: string | boolean) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    // Clear error for this field when user starts typing
    if (errors[field as keyof FormErrors]) {
      setErrors((prev) => ({ ...prev, [field]: undefined }));
    }
  };

  return (
    <Card className="max-w-md mx-auto">
      <CardHeader>
        <CardTitle>Create Account</CardTitle>
        <CardDescription>
          Sign up to get started with ConsultantOS
        </CardDescription>
      </CardHeader>

      <CardContent>
        {successMessage && (
          <Alert
            variant="success"
            title="Success!"
            description={successMessage}
            dismissible
            onClose={() => setSuccessMessage("")}
            className="mb-4"
          />
        )}

        {errorMessage && (
          <Alert
            variant="error"
            title="Registration Failed"
            description={errorMessage}
            dismissible
            onClose={() => setErrorMessage("")}
            className="mb-4"
          />
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Full Name"
            leftIcon={<User className="w-5 h-5" />}
            value={formData.name}
            onChange={(e) => handleChange("name", e.target.value)}
            error={errors.name}
            placeholder="John Doe"
            required
            fullWidth
            disabled={isLoading}
          />

          <Input
            label="Email Address"
            type="email"
            leftIcon={<Mail className="w-5 h-5" />}
            value={formData.email}
            onChange={(e) => handleChange("email", e.target.value)}
            error={errors.email}
            placeholder="you@example.com"
            required
            fullWidth
            disabled={isLoading}
          />

          <div>
            <Input
              label="Password"
              type="password"
              leftIcon={<Lock className="w-5 h-5" />}
              value={formData.password}
              onChange={(e) => handleChange("password", e.target.value)}
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
                  <span
                    className={`font-medium ${
                      passwordStrength.score <= 2
                        ? "text-red-600"
                        : passwordStrength.score === 3
                        ? "text-yellow-600"
                        : passwordStrength.score === 4
                        ? "text-blue-600"
                        : "text-green-600"
                    }`}
                  >
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
            label="Confirm Password"
            type="password"
            leftIcon={<Lock className="w-5 h-5" />}
            value={formData.confirmPassword}
            onChange={(e) => handleChange("confirmPassword", e.target.value)}
            error={errors.confirmPassword}
            placeholder="Re-enter password"
            required
            fullWidth
            disabled={isLoading}
          />

          <div>
            <label className="flex items-start gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={formData.termsAccepted}
                onChange={(e) =>
                  handleChange("termsAccepted", e.target.checked)
                }
                disabled={isLoading}
                className="mt-0.5 h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
              />
              <span className="text-sm text-gray-700">
                I agree to the{" "}
                <a href="/terms" className="text-primary-600 hover:underline">
                  Terms and Conditions
                </a>{" "}
                and{" "}
                <a href="/privacy" className="text-primary-600 hover:underline">
                  Privacy Policy
                </a>
              </span>
            </label>
            {errors.termsAccepted && (
              <p className="text-sm text-red-600 mt-1">
                {errors.termsAccepted}
              </p>
            )}
          </div>

          <Button
            type="submit"
            fullWidth
            isLoading={isLoading}
            disabled={isLoading}
          >
            Create Account
          </Button>

          <p className="text-sm text-center text-gray-600">
            Already have an account?{" "}
            <a
              href="/login"
              className="text-primary-600 hover:underline font-medium"
            >
              Sign in
            </a>
          </p>
        </form>
      </CardContent>
    </Card>
  );
};
