# User Management Components

Complete set of user authentication and profile management components for ConsultantOS frontend.

## Components Overview

All components follow Phase 1 design patterns and use the existing component library (Input, Button, Card, Alert).

### 1. RegistrationForm

User signup form with comprehensive validation and password strength indicator.

**Features:**
- Email validation with regex pattern
- Real-time password strength indicator (Weak/Fair/Good/Strong)
- Password confirmation matching
- Terms and conditions acceptance
- Success message with email verification prompt
- Loading states during API calls

**Props:**
```typescript
interface RegistrationFormProps {
  onSuccess?: (email: string) => void;
  apiUrl?: string;
}
```

**Usage:**
```tsx
import { RegistrationForm } from '@/app/components/RegistrationForm';

<RegistrationForm
  onSuccess={(email) => {
    console.log('User registered:', email);
    router.push(`/verify-email?email=${email}`);
  }}
  apiUrl="http://localhost:8080"
/>
```

**API Endpoint:** `POST /users/register`

**Validation:**
- Name: Required, non-empty
- Email: Required, valid email format
- Password: Min 8 characters
- Confirm Password: Must match password
- Terms: Must be accepted

---

### 2. EmailVerification

Email verification UI with 6-digit code input and resend functionality.

**Features:**
- 6-digit numeric code input
- Resend code with 60-second countdown
- Auto-validation of code format
- Success state with redirect
- Error handling

**Props:**
```typescript
interface EmailVerificationProps {
  email?: string;
  onSuccess?: () => void;
  apiUrl?: string;
}
```

**Usage:**
```tsx
import { EmailVerification } from '@/app/components/EmailVerification';

<EmailVerification
  email="user@example.com"
  onSuccess={() => router.push('/login')}
  apiUrl="http://localhost:8080"
/>
```

**API Endpoints:**
- `POST /users/verify-email` - Verify code
- `POST /users/resend-verification` - Resend code

---

### 3. PasswordResetForm

Password reset request form that sends reset instructions via email.

**Features:**
- Email validation
- Simple, clean interface
- Success message with instructions
- Back to login link
- Error handling

**Props:**
```typescript
interface PasswordResetFormProps {
  onSuccess?: (email: string) => void;
  apiUrl?: string;
}
```

**Usage:**
```tsx
import { PasswordResetForm } from '@/app/components/PasswordResetForm';

<PasswordResetForm
  onSuccess={(email) => {
    console.log('Reset email sent to:', email);
  }}
  apiUrl="http://localhost:8080"
/>
```

**API Endpoint:** `POST /users/request-password-reset`

---

### 4. PasswordResetConfirm

New password setting form with token validation.

**Features:**
- Token validation on mount
- Password strength indicator with requirements checklist
- Visual strength meter
- Password confirmation matching
- Invalid token handling with redirect
- Detailed password requirements display

**Props:**
```typescript
interface PasswordResetConfirmProps {
  token?: string;
  onSuccess?: () => void;
  apiUrl?: string;
}
```

**Usage:**
```tsx
import { PasswordResetConfirm } from '@/app/components/PasswordResetConfirm';

// Get token from URL params
const searchParams = useSearchParams();
const token = searchParams.get('token');

<PasswordResetConfirm
  token={token}
  onSuccess={() => router.push('/login')}
  apiUrl="http://localhost:8080"
/>
```

**API Endpoint:** `POST /users/reset-password`

**Password Requirements:**
- Minimum 8 characters
- Upper and lowercase letters
- At least one number
- Special character (recommended)
- Strength score ≥ 3 (Fair or better)

---

### 5. ProfileSettings

Comprehensive user profile management dashboard.

**Features:**
- View and edit profile (name, email)
- Change password section with strength indicator
- Account deletion with confirmation modal
- Loading states for all operations
- Member since date display
- Danger zone for destructive actions

**Props:**
```typescript
interface ProfileSettingsProps {
  apiKey?: string;
  onProfileUpdate?: () => void;
  onAccountDelete?: () => void;
  apiUrl?: string;
}
```

**Usage:**
```tsx
import { ProfileSettings } from '@/app/components/ProfileSettings';

<ProfileSettings
  apiKey={userApiKey}
  onProfileUpdate={() => {
    console.log('Profile updated');
    fetchUserData();
  }}
  onAccountDelete={() => {
    console.log('Account deleted');
    router.push('/');
  }}
  apiUrl="http://localhost:8080"
/>
```

**API Endpoints:**
- `GET /users/profile` - Fetch profile
- `PUT /users/profile` - Update profile
- `POST /users/change-password` - Change password
- `DELETE /users/profile` - Delete account

**Sections:**
1. Profile Information - Name, email, member since
2. Change Password - Current password, new password with strength indicator
3. Danger Zone - Account deletion with confirmation

---

## Common Features

All components include:

- **TypeScript Support** - Full type safety with interfaces
- **Client-side Validation** - Immediate feedback before API calls
- **Loading States** - Visual feedback during async operations
- **Error Handling** - User-friendly error messages via Alert
- **Success Notifications** - Confirmation of successful actions
- **Accessibility** - ARIA labels, keyboard navigation, focus management
- **Responsive Design** - Mobile-first approach
- **Consistent Styling** - Using Phase 1 component library

## Validation Utilities

### Email Validation
```typescript
const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};
```

### Password Strength Calculation
```typescript
const getPasswordStrength = (password: string): {
  score: number;
  label: string;
  color: string;
} => {
  let score = 0;

  if (password.length >= 8) score++;
  if (password.length >= 12) score++;
  if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score++;
  if (/\d/.test(password)) score++;
  if (/[^A-Za-z0-9]/.test(password)) score++;

  // Returns: { score: 0-5, label: 'Weak'|'Fair'|'Good'|'Strong', color: 'bg-...' }
};
```

## Integration Example

Complete authentication flow:

```tsx
// app/register/page.tsx
import { RegistrationForm } from '@/app/components/user-management';

export default function RegisterPage() {
  const router = useRouter();

  return (
    <RegistrationForm
      onSuccess={(email) => {
        router.push(`/verify-email?email=${encodeURIComponent(email)}`);
      }}
    />
  );
}

// app/verify-email/page.tsx
import { EmailVerification } from '@/app/components/user-management';

export default function VerifyEmailPage() {
  const searchParams = useSearchParams();
  const email = searchParams.get('email');
  const router = useRouter();

  return (
    <EmailVerification
      email={email || ''}
      onSuccess={() => router.push('/login')}
    />
  );
}

// app/profile/page.tsx
import { ProfileSettings } from '@/app/components/user-management';

export default function ProfilePage() {
  const { apiKey } = useAuth(); // Your auth hook

  return (
    <ProfileSettings
      apiKey={apiKey}
      onAccountDelete={() => {
        // Logout and redirect
        logout();
        router.push('/');
      }}
    />
  );
}
```

## Environment Variables

Configure API URL in `.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8080
```

## File Paths

All components are located in:

```
/Users/rish2jain/Documents/Hackathons/ConsultantOS/frontend/app/components/
├── RegistrationForm.tsx
├── EmailVerification.tsx
├── PasswordResetForm.tsx
├── PasswordResetConfirm.tsx
├── ProfileSettings.tsx
└── user-management/
    ├── index.ts (barrel export)
    └── README.md (this file)
```

## Component Dependencies

All components use:
- `Input` from `./Input`
- `Button` from `./Button`
- `Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter` from `./Card`
- `Alert` from `./Alert`
- `Modal` from `./Modal` (ProfileSettings only)
- `lucide-react` icons

## Backend API Contract

Expected request/response formats:

### POST /users/register
```typescript
Request: { email: string; password: string; name: string }
Response: { message: string; user_id: string }
```

### POST /users/verify-email
```typescript
Request: { email: string; code: string }
Response: { message: string }
```

### POST /users/request-password-reset
```typescript
Request: { email: string }
Response: { message: string }
```

### POST /users/reset-password
```typescript
Request: { token: string; new_password: string }
Response: { message: string }
```

### GET /users/profile
```typescript
Headers: { 'X-API-Key': string }
Response: { email: string; name: string; created_at: string }
```

### PUT /users/profile
```typescript
Headers: { 'X-API-Key': string }
Request: { name: string; email: string }
Response: { email: string; name: string; created_at: string }
```

### POST /users/change-password
```typescript
Headers: { 'X-API-Key': string }
Request: { current_password: string; new_password: string }
Response: { message: string }
```

### DELETE /users/profile
```typescript
Headers: { 'X-API-Key': string }
Response: { message: string }
```

## Testing

Components can be tested with:

```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { RegistrationForm } from './RegistrationForm';

test('validates email format', async () => {
  render(<RegistrationForm />);

  const emailInput = screen.getByLabelText(/email/i);
  fireEvent.change(emailInput, { target: { value: 'invalid-email' } });
  fireEvent.blur(emailInput);

  await waitFor(() => {
    expect(screen.getByText(/valid email/i)).toBeInTheDocument();
  });
});
```

## Accessibility Features

- All form fields have proper labels
- Error messages linked via `aria-describedby`
- Loading states announced to screen readers
- Keyboard navigation support
- Focus management in modals
- ARIA roles and attributes
- Color contrast compliance

## Browser Support

Compatible with:
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)
