'use client';

import { PasswordResetForm } from '@/app/components/PasswordResetForm';
import Link from 'next/link';

export default function ResetPasswordPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Logo and Title */}
        <div className="text-center">
          <h1 className="text-4xl font-bold text-primary-600">ConsultantOS</h1>
          <p className="mt-2 text-sm text-gray-600">
            Reset your password
          </p>
        </div>

        {/* Password Reset Form */}
        <PasswordResetForm
          onSuccess={(email) => {
            console.log('Password reset email sent to:', email);
          }}
        />

        {/* Back to Login Link */}
        <div className="text-center">
          <Link
            href="/login"
            className="text-sm text-primary-600 hover:text-primary-500 transition-colors"
          >
            Back to Sign In
          </Link>
        </div>
      </div>
    </div>
  );
}

