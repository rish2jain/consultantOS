# Analysis Request Form Components

Comprehensive form components for submitting business analysis requests to the ConsultantOS backend.

## Overview

This suite of components provides a complete user interface for creating analysis requests with validation, accessibility, and an excellent user experience.

## Components

### 1. AnalysisRequestForm

Main form component that integrates all selectors and handles submission.

**File**: `AnalysisRequestForm.tsx`

**Features**:
- Complete form integration with all field validators
- Real-time validation with field-specific error messages
- Loading states during submission
- Success/error alerts with dismissible notifications
- Support for both sync and async analysis requests
- Reset functionality to clear all fields
- Character counters for text fields
- Responsive layout with mobile support

**Usage**:
```tsx
import { AnalysisRequestForm } from '@/app/components';

function MyPage() {
  const handleSuccess = (reportData) => {
    console.log('Analysis created:', reportData);
  };

  const handleError = (error) => {
    console.error('Analysis failed:', error);
  };

  return (
    <AnalysisRequestForm
      apiKey="your-api-key-here" // Optional
      onSuccess={handleSuccess}
      onError={handleError}
      async={false} // false = wait for completion, true = return job_id
    />
  );
}
```

**Props**:
```typescript
interface AnalysisRequestFormProps {
  apiKey?: string;              // Optional API key for authenticated requests
  onSuccess?: (data: any) => void; // Callback when submission succeeds
  onError?: (error: Error) => void; // Callback when submission fails
  async?: boolean;              // Use async endpoint (default: false)
}
```

**Form Fields**:
- **Company** (required): Text input with icon, 2-100 characters
- **Industry** (required): Searchable dropdown selector
- **Frameworks** (required): Multi-select with visual cards, 1-4 selections
- **Depth**: Radio group for analysis depth (quick/standard/deep)
- **Region** (optional): Text input, up to 100 characters
- **Additional Context** (optional): Textarea, up to 1000 characters

**Validation Rules**:
- Company: Required, 2-100 characters
- Industry: Required
- Frameworks: Required, 1-4 selections
- Region: Optional, max 100 characters
- Additional Context: Optional, max 1000 characters

**API Integration**:
- Endpoint: `POST /analyze` (sync) or `POST /analyze/async`
- Headers: `Content-Type: application/json`, optional `X-API-Key`
- Timeout: 5 minutes for sync, 30 seconds for async
- Error handling with user-friendly messages

---

### 2. FrameworkSelector

Multi-select component for business framework selection with visual cards.

**File**: `FrameworkSelector.tsx`

**Features**:
- Visual card-based selection interface
- Icons and descriptions for each framework
- Selected state with checkmarks and highlighting
- Keyboard navigation support
- ARIA labels for accessibility
- Responsive grid layout

**Available Frameworks**:
1. **Porter's Five Forces** - Analyze competitive intensity and attractiveness
2. **SWOT Analysis** - Identify strengths, weaknesses, opportunities, threats
3. **PESTEL Analysis** - Examine political, economic, social, technological, environmental, legal factors
4. **Blue Ocean Strategy** - Discover uncontested market spaces

**Usage**:
```tsx
import { FrameworkSelector } from '@/app/components';

function MyComponent() {
  const [frameworks, setFrameworks] = useState([]);

  return (
    <FrameworkSelector
      value={frameworks}
      onChange={setFrameworks}
      error={errors.frameworks}
      disabled={false}
      required={true}
    />
  );
}
```

**Props**:
```typescript
interface FrameworkSelectorProps {
  value: ('porter' | 'swot' | 'pestel' | 'blue_ocean')[];
  onChange: (frameworks: Array) => void;
  error?: string;
  disabled?: boolean;
  required?: boolean;
}
```

**Accessibility**:
- Role: `group`
- Each card: `button` with `aria-pressed`
- Keyboard: Space/Enter to toggle selection
- Screen reader: Full descriptions announced

---

### 3. IndustrySelector

Searchable dropdown component for industry selection.

**File**: `IndustrySelector.tsx`

**Features**:
- 28 predefined industry options
- Real-time search/filter functionality
- Keyboard navigation (Arrow keys, Enter, Escape, Tab)
- Click-outside detection to close dropdown
- Selected state with checkmark indicator
- Highlighted option on keyboard navigation
- Auto-focus search input when opened

**Industry Options**:
Technology, Healthcare, Finance, Retail, Manufacturing, Energy, Telecommunications, Transportation, Real Estate, Automotive, Aerospace, Agriculture, Biotechnology, Construction, Consumer Goods, E-commerce, Education, Entertainment, Food & Beverage, Hospitality, Insurance, Legal Services, Media, Pharmaceuticals, Professional Services, Software, Utilities, Other

**Usage**:
```tsx
import { IndustrySelector } from '@/app/components';

function MyComponent() {
  const [industry, setIndustry] = useState('');

  return (
    <IndustrySelector
      value={industry}
      onChange={setIndustry}
      error={errors.industry}
      disabled={false}
      required={true}
      placeholder="Select an industry..."
    />
  );
}
```

**Props**:
```typescript
interface IndustrySelectorProps {
  value: string;
  onChange: (industry: string) => void;
  error?: string;
  disabled?: boolean;
  required?: boolean;
  placeholder?: string;
}
```

**Keyboard Controls**:
- `Enter`: Select highlighted option or open dropdown
- `Arrow Down`: Navigate to next option
- `Arrow Up`: Navigate to previous option
- `Escape`: Close dropdown
- `Tab`: Close dropdown and move focus
- Typing: Filter options in real-time

**Accessibility**:
- Role: `listbox` with `option` items
- `aria-haspopup`, `aria-expanded` on trigger button
- `aria-selected` on options
- `aria-describedby` for error messages

---

### 4. DepthSelector

Radio group component for selecting analysis depth.

**File**: `DepthSelector.tsx`

**Features**:
- Three analysis depth options
- Visual card-based radio buttons
- Icons and time estimates for each option
- Custom radio indicator with animation
- Keyboard support (Enter, Space)
- Responsive grid layout (1 column mobile, 3 columns desktop)

**Depth Options**:
1. **Quick Analysis** (~10 minutes) - High-level overview with key insights
2. **Standard Analysis** (~20 minutes) - Balanced depth with comprehensive coverage
3. **Deep Analysis** (~30 minutes) - Thorough investigation with detailed insights

**Usage**:
```tsx
import { DepthSelector } from '@/app/components';

function MyComponent() {
  const [depth, setDepth] = useState<'quick' | 'standard' | 'deep'>('standard');

  return (
    <DepthSelector
      value={depth}
      onChange={setDepth}
      error={errors.depth}
      disabled={false}
    />
  );
}
```

**Props**:
```typescript
interface DepthSelectorProps {
  value: 'quick' | 'standard' | 'deep';
  onChange: (depth: 'quick' | 'standard' | 'deep') => void;
  error?: string;
  disabled?: boolean;
}
```

**Accessibility**:
- Role: `radiogroup` with `radio` items
- Hidden native radio inputs for form compatibility
- Labels with `aria-describedby` for descriptions
- Keyboard: Space/Enter on labels to select
- Focus management with `tabIndex`

---

## Design System Integration

All components follow the ConsultantOS design system established in Phase 1:

**Colors**:
- Primary: `primary-500`, `primary-600`, `primary-700`
- Success: `green-500`, `green-600`
- Error: `red-500`, `red-600`
- Neutral: `gray-50` through `gray-900`

**Typography**:
- Labels: `text-sm font-medium text-gray-700`
- Headings: `text-base font-semibold text-gray-900`
- Descriptions: `text-sm text-gray-600`
- Helper text: `text-xs text-gray-500`
- Errors: `text-sm text-red-600`

**Spacing**:
- Form fields: `mb-1` for labels, `mt-2` for helper text
- Cards: `p-4` for content, `gap-3` between elements
- Grid gaps: `gap-4` for responsive layouts

**Transitions**:
- All interactive elements: `transition-all duration-200`
- Hover effects: `hover:shadow-md`, `hover:scale-[1.01]`
- Focus states: `focus:ring-2 focus:ring-primary-500`

**Icons**:
- Size: `w-5 h-5` for form icons
- Source: `lucide-react` package
- Accessibility: `aria-hidden="true"` on decorative icons

---

## Accessibility Features

All components meet WCAG 2.1 AA standards:

**Keyboard Navigation**:
- Full keyboard support for all interactions
- Logical tab order
- Enter/Space for activation
- Arrow keys for option navigation
- Escape to dismiss dropdowns

**Screen Readers**:
- Semantic HTML with proper roles
- ARIA labels and descriptions
- Live regions for dynamic content
- Error announcements with `role="alert"`

**Visual Accessibility**:
- Sufficient color contrast (4.5:1 minimum)
- Focus indicators on all interactive elements
- Error states with multiple cues (color + icon + text)
- No reliance on color alone for information

**Form Accessibility**:
- Labels associated with inputs
- Required field indicators
- Error messages linked via `aria-describedby`
- Helper text for additional context

---

## Responsive Design

Components adapt to different screen sizes:

**Mobile (< 640px)**:
- Single column layouts
- Full-width inputs and buttons
- Stacked form actions
- Touch-friendly tap targets (minimum 44x44px)

**Tablet (640px - 1024px)**:
- 2-column depth selector
- Optimized spacing
- Flexible card layouts

**Desktop (> 1024px)**:
- 3-column depth selector
- Maximum width: `max-w-4xl`
- Side-by-side form actions

---

## Error Handling

**Client-Side Validation**:
- Real-time validation on blur/change
- Field-specific error messages
- Required field enforcement
- Length constraints
- Pattern matching (where applicable)

**Server-Side Errors**:
- HTTP error code handling
- User-friendly error messages
- Detailed error from `response.data.detail`
- Fallback generic messages
- Error alerts with dismiss option

**Error Display**:
- Inline field errors (red text below input)
- Top-level submit errors (Alert component)
- Icon indicators (AlertCircle, CheckCircle)
- ARIA announcements for screen readers

---

## Performance Considerations

**Optimizations**:
- Debounced search in IndustrySelector
- Event delegation where applicable
- Minimal re-renders with proper state management
- Lazy evaluation of validation rules

**Bundle Size**:
- Tree-shakeable exports
- Shared component reuse (Card, Input, Button)
- Lucide-react for lightweight icons

**Runtime Performance**:
- Efficient keyboard event handling
- Click-outside detection with cleanup
- Proper useEffect dependencies
- No unnecessary DOM queries

---

## Testing Guidelines

**Unit Tests**:
```typescript
// Test validation logic
describe('AnalysisRequestForm validation', () => {
  it('requires company name', () => {
    // Test required field validation
  });

  it('enforces framework selection', () => {
    // Test at least 1 framework required
  });

  it('respects character limits', () => {
    // Test maxLength validation
  });
});
```

**Integration Tests**:
```typescript
// Test form submission
describe('AnalysisRequestForm submission', () => {
  it('submits valid form data', async () => {
    // Mock axios, submit form, verify API call
  });

  it('handles API errors gracefully', async () => {
    // Mock API error, verify error display
  });
});
```

**Accessibility Tests**:
```typescript
// Test keyboard navigation
describe('IndustrySelector accessibility', () => {
  it('supports keyboard navigation', () => {
    // Test ArrowDown, Enter, Escape
  });

  it('announces selection to screen readers', () => {
    // Test ARIA attributes
  });
});
```

---

## Example: Complete Integration

```tsx
'use client';

import { useState } from 'react';
import { AnalysisRequestForm } from '@/app/components';

export default function AnalysisPage() {
  const [reportData, setReportData] = useState(null);

  const handleSuccess = (data) => {
    console.log('Analysis completed:', data);
    setReportData(data);
    // Optionally redirect to report page
    // router.push(`/reports/${data.report_id}`);
  };

  const handleError = (error) => {
    console.error('Analysis failed:', error);
    // Error is already displayed in the form
    // Optionally log to error tracking service
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Business Analysis Request
          </h1>
          <p className="mt-2 text-gray-600">
            Generate comprehensive strategic insights in minutes
          </p>
        </div>

        <AnalysisRequestForm
          apiKey={sessionStorage.getItem('apiKey')}
          onSuccess={handleSuccess}
          onError={handleError}
          async={false}
        />

        {reportData && (
          <div className="mt-8 p-6 bg-white rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">
              Analysis Complete
            </h2>
            <p className="text-gray-600">
              Report ID: {reportData.report_id}
            </p>
            {reportData.pdf_url && (
              <a
                href={reportData.pdf_url}
                target="_blank"
                rel="noopener noreferrer"
                className="mt-4 inline-block text-primary-600 hover:underline"
              >
                Download PDF Report →
              </a>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
```

---

## API Contract

**Request**:
```typescript
POST /analyze

Headers:
  Content-Type: application/json
  X-API-Key: <optional-api-key>

Body:
{
  "company": "Tesla",
  "industry": "Automotive",
  "frameworks": ["porter", "swot", "pestel"],
  "depth": "standard",
  "additional_context": "Focus on EV market competition",
  "region": "North America"
}
```

**Response (Success)**:
```typescript
{
  "report_id": "uuid-here",
  "company": "Tesla",
  "industry": "Automotive",
  "frameworks": ["porter", "swot", "pestel"],
  "status": "completed",
  "confidence_score": 0.92,
  "created_at": "2024-01-15T10:30:00Z",
  "execution_time_seconds": 187.5,
  "pdf_url": "https://storage.googleapis.com/...",
  "framework_analysis": {
    "porter_five_forces": { ... },
    "swot_analysis": { ... },
    "pestel_analysis": { ... }
  }
}
```

**Response (Error)**:
```typescript
{
  "detail": "Company name is required"
}
```

---

## Future Enhancements

Potential improvements for future iterations:

1. **Template Support**: Save and load analysis templates
2. **Batch Requests**: Analyze multiple companies at once
3. **Custom Frameworks**: Allow users to define custom analysis frameworks
4. **Collaboration**: Share draft requests with team members
5. **History**: Show previous analyses for the same company
6. **Smart Defaults**: Pre-fill fields based on user history
7. **Framework Recommendations**: AI-suggested frameworks based on industry
8. **Progress Indicators**: Real-time updates during async analysis
9. **Draft Saving**: Auto-save form state to localStorage
10. **Export Options**: Additional formats (Excel, Word, JSON)

---

## Troubleshooting

**Common Issues**:

1. **API key not working**
   - Verify API key is valid and not expired
   - Check X-API-Key header is being sent
   - Ensure user has permission for analysis endpoint

2. **Validation errors not clearing**
   - Verify onChange handlers update state correctly
   - Check error state management in parent component

3. **Dropdown not closing**
   - Verify click-outside detection is working
   - Check for z-index conflicts with other elements

4. **Submission timeout**
   - Increase axios timeout for slow networks
   - Consider using async mode for long analyses

5. **TypeScript errors**
   - Ensure all prop types match interface definitions
   - Check import paths are correct (@/app/components)

---

## Dependencies

Required packages (already installed in ConsultantOS):
- `react` - Core React library
- `axios` - HTTP client for API requests
- `lucide-react` - Icon library
- `tailwindcss` - Styling framework

Peer dependencies from existing components:
- `@/app/components` - Button, Input, Card, Alert

---

## File Paths

All component files are located in:
```
/Users/rish2jain/Documents/Hackathons/ConsultantOS/frontend/app/components/
```

- `FrameworkSelector.tsx` - Framework multi-select component
- `IndustrySelector.tsx` - Industry searchable dropdown
- `DepthSelector.tsx` - Analysis depth radio selector
- `AnalysisRequestForm.tsx` - Main form integrating all components
- `index.ts` - Component exports (updated)
