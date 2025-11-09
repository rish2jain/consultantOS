# ConsultantOS UI Component Library

Production-ready React components built with TypeScript, Tailwind CSS, and accessibility in mind.

## Installation

All components are available via the central export:

```typescript
import { Button, Input, Card, Alert } from '@/app/components';
```

## Component Catalog

### Core Components

#### Button
Versatile button component with multiple variants and states.

```typescript
import { Button } from '@/app/components';

// Primary button
<Button variant="primary" onClick={handleClick}>
  Click me
</Button>

// With loading state
<Button isLoading>Loading...</Button>

// With icons
<Button leftIcon={<PlusIcon />} rightIcon={<ArrowIcon />}>
  Add Item
</Button>
```

**Props:**
- `variant`: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger'
- `size`: 'sm' | 'md' | 'lg'
- `isLoading`: boolean
- `leftIcon`, `rightIcon`: ReactNode
- `fullWidth`: boolean
- `disabled`: boolean

---

#### Input
Advanced input field with validation and password toggle.

```typescript
import { Input, PasswordInput } from '@/app/components';

// Basic input
<Input
  label="Email"
  type="email"
  placeholder="Enter your email"
  helperText="We'll never share your email"
/>

// With error
<Input
  label="Username"
  error="Username is already taken"
/>

// Password input with toggle
<PasswordInput
  label="Password"
  showCounter
  maxLength={50}
/>

// With icons
<Input
  leftIcon={<SearchIcon />}
  placeholder="Search..."
/>
```

**Props:**
- `label`: string
- `helperText`: string
- `error`: string
- `success`: boolean
- `size`: 'sm' | 'md' | 'lg'
- `leftIcon`, `rightIcon`: ReactNode
- `fullWidth`: boolean
- `showCounter`: boolean
- `maxLength`: number

---

#### Card
Flexible card container with compound components.

```typescript
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter
} from '@/app/components';

<Card variant="elevated" hoverable>
  <CardHeader>
    <CardTitle>Dashboard</CardTitle>
    <CardDescription>Overview of your metrics</CardDescription>
  </CardHeader>
  <CardContent>
    {/* Your content */}
  </CardContent>
  <CardFooter>
    <Button>View Details</Button>
  </CardFooter>
</Card>
```

**Props:**
- `variant`: 'default' | 'outlined' | 'elevated' | 'filled'
- `padding`: 'none' | 'sm' | 'md' | 'lg'
- `hoverable`: boolean
- `clickable`: boolean
- `selected`: boolean

---

#### MetricCard
Enhanced card for displaying KPIs with trends.

```typescript
import { MetricCard } from '@/app/components';

<MetricCard
  title="Total Revenue"
  value="$45,231"
  icon={<DollarSignIcon />}
  color="green"
  trend="up"
  trendValue="12.5%"
  subtitle="vs last month"
  onClick={() => navigate('/revenue')}
/>
```

**Props:**
- `title`: string
- `value`: string | number
- `icon`: ReactNode
- `color`: 'blue' | 'green' | 'purple' | 'orange' | 'red' | 'gray'
- `trend`: 'up' | 'down' | 'neutral'
- `trendValue`: string
- `subtitle`: string
- `isLoading`: boolean
- `onClick`: function

---

#### Modal
Accessible modal dialog with focus trap.

```typescript
import { Modal, useModal } from '@/app/components';

function MyComponent() {
  const { isOpen, open, close } = useModal();

  return (
    <>
      <Button onClick={open}>Open Modal</Button>
      <Modal
        isOpen={isOpen}
        onClose={close}
        title="Confirm Action"
        description="Are you sure you want to proceed?"
        size="md"
        footer={
          <>
            <Button variant="ghost" onClick={close}>Cancel</Button>
            <Button variant="primary" onClick={handleConfirm}>Confirm</Button>
          </>
        }
      >
        <p>This action cannot be undone.</p>
      </Modal>
    </>
  );
}
```

**Props:**
- `isOpen`: boolean
- `onClose`: function
- `title`: string
- `description`: string
- `size`: 'sm' | 'md' | 'lg' | 'xl' | 'full'
- `showCloseButton`: boolean
- `closeOnOverlayClick`: boolean
- `closeOnEscape`: boolean
- `footer`: ReactNode

---

#### Badge
Status badges with variants.

```typescript
import { Badge } from '@/app/components';

<Badge variant="success" size="sm">
  Active
</Badge>

<Badge variant="warning" dot>
  Pending
</Badge>

<Badge variant="danger" removable onRemove={handleRemove}>
  Error
</Badge>
```

**Props:**
- `variant`: 'default' | 'primary' | 'success' | 'warning' | 'danger' | 'info'
- `size`: 'sm' | 'md' | 'lg'
- `removable`: boolean
- `onRemove`: function
- `dot`: boolean

---

### Interactive Components

#### Dropdown
Dropdown menu with keyboard navigation.

```typescript
import { Dropdown, useDropdown } from '@/app/components';

const items = [
  { label: 'Edit', value: 'edit', icon: <EditIcon /> },
  { label: 'Delete', value: 'delete', icon: <TrashIcon />, disabled: false },
];

<Dropdown
  items={items}
  value={selectedValue}
  onChange={setSelectedValue}
  placement="bottom-start"
  width="trigger"
/>

// Custom trigger
<Dropdown
  items={items}
  trigger={<Button>Actions</Button>}
/>

// With hook
const dropdown = useDropdown();
<Dropdown
  items={items}
  value={dropdown.selectedValue}
  onChange={dropdown.select}
/>
```

**Props:**
- `items`: DropdownItem[]
- `trigger`: ReactNode
- `value`: string
- `onChange`: function
- `placement`: 'bottom-start' | 'bottom-end' | 'top-start' | 'top-end'
- `width`: 'auto' | 'full' | 'trigger'
- `disabled`: boolean

---

#### Tabs
Tab navigation with horizontal/vertical layouts.

```typescript
import { Tabs, TabList, Tab, TabPanels, TabPanel, useTabs } from '@/app/components';

<Tabs defaultValue="profile" orientation="horizontal">
  <TabList>
    <Tab value="profile">Profile</Tab>
    <Tab value="settings">Settings</Tab>
    <Tab value="billing">Billing</Tab>
  </TabList>

  <TabPanels>
    <TabPanel value="profile">
      <ProfileContent />
    </TabPanel>
    <TabPanel value="settings">
      <SettingsContent />
    </TabPanel>
    <TabPanel value="billing">
      <BillingContent />
    </TabPanel>
  </TabPanels>
</Tabs>

// Controlled mode
const { activeTab, setActiveTab } = useTabs('profile');
<Tabs value={activeTab} onValueChange={setActiveTab}>
  {/* tabs */}
</Tabs>
```

**Props:**
- `defaultValue`: string (uncontrolled)
- `value`: string (controlled)
- `onValueChange`: function
- `orientation`: 'horizontal' | 'vertical'

---

#### Tooltip
Context-aware tooltips with positioning.

```typescript
import { Tooltip, SimpleTooltip } from '@/app/components';

<Tooltip content="Click to edit" placement="top" delay={200}>
  <Button>Edit</Button>
</Tooltip>

// Simple text tooltip
<SimpleTooltip text="Help text" placement="right">
  <InfoIcon />
</SimpleTooltip>

// Custom content
<Tooltip
  content={
    <div>
      <strong>Advanced Settings</strong>
      <p>Configure advanced options</p>
    </div>
  }
  showArrow
  maxWidth="300px"
>
  <Button>Settings</Button>
</Tooltip>
```

**Props:**
- `content`: ReactNode
- `placement`: 'top' | 'bottom' | 'left' | 'right'
- `delay`: number (ms)
- `showArrow`: boolean
- `disabled`: boolean
- `maxWidth`: string

---

### Feedback Components

#### Alert
Alert banners with variants and actions.

```typescript
import {
  Alert,
  InfoAlert,
  SuccessAlert,
  WarningAlert,
  ErrorAlert,
  useAlert
} from '@/app/components';

// Basic alerts
<InfoAlert title="Information" description="This is an informational message" />
<SuccessAlert title="Success!" description="Operation completed successfully" />
<WarningAlert title="Warning" description="Please review before proceeding" />
<ErrorAlert title="Error" description="Something went wrong" />

// Dismissible with auto-dismiss
<Alert
  variant="info"
  title="Auto-dismiss"
  description="This will disappear in 5 seconds"
  dismissible
  autoDismiss={5000}
  onClose={handleClose}
/>

// With actions
<Alert
  variant="warning"
  title="Confirm Action"
  actions={
    <>
      <Button size="sm" variant="outline">Cancel</Button>
      <Button size="sm" variant="primary">Confirm</Button>
    </>
  }
>
  Are you sure you want to delete this item?
</Alert>

// Using hook for programmatic alerts
function MyComponent() {
  const alert = useAlert();

  const handleSuccess = () => {
    alert.success('Success!', 'Data saved successfully');
  };

  return (
    <>
      <Button onClick={handleSuccess}>Save</Button>
      {alert.alerts.map(a => (
        <Alert
          key={a.id}
          variant={a.variant}
          title={a.title}
          description={a.description}
          dismissible
          onClose={() => alert.hideAlert(a.id)}
        />
      ))}
    </>
  );
}
```

**Props:**
- `variant`: 'info' | 'success' | 'warning' | 'error'
- `title`: string
- `description`: string | ReactNode
- `dismissible`: boolean
- `onClose`: function
- `autoDismiss`: number (ms)
- `showIcon`: boolean
- `actions`: ReactNode

---

#### Spinner
Loading spinners with variants.

```typescript
import {
  Spinner,
  PrimarySpinner,
  WhiteSpinner,
  LoadingOverlay,
  InlineLoading
} from '@/app/components';

// Basic spinner
<Spinner size="md" color="primary" variant="circular" />

// Different variants
<Spinner variant="dots" size="lg" />
<Spinner variant="bars" color="gray" />
<Spinner variant="pulse" size="xl" />

// Preset spinners
<PrimarySpinner size="md" />
<WhiteSpinner size="lg" />

// Full page overlay
<LoadingOverlay
  isLoading={isLoading}
  message="Loading data..."
  size="lg"
  blur
/>

// Inline loading
<InlineLoading
  message="Fetching results..."
  size="sm"
  centered
/>
```

**Props:**
- `size`: 'sm' | 'md' | 'lg' | 'xl'
- `color`: 'primary' | 'white' | 'gray' | 'inherit'
- `variant`: 'circular' | 'dots' | 'bars' | 'pulse'
- `label`: string (accessibility)

---

## Accessibility Features

All components follow WCAG 2.1 AA standards:

- **Keyboard Navigation**: Tab, Arrow keys, Enter, Escape
- **ARIA Labels**: Proper roles and labels for screen readers
- **Focus Management**: Visible focus indicators and focus trapping
- **Color Contrast**: Sufficient contrast ratios
- **Screen Reader Support**: Descriptive text and state announcements

## TypeScript Support

All components are fully typed with TypeScript:

```typescript
import type { ButtonProps, InputProps, ModalProps } from '@/app/components';

const myButtonProps: ButtonProps = {
  variant: 'primary',
  size: 'md',
  isLoading: false,
};
```

## Styling

Components use Tailwind CSS with customizable variants. To extend or modify:

1. Update `tailwind.config.js` for global theme changes
2. Pass custom `className` prop for component-specific styles
3. Use variant props for predefined style options

## Usage Examples

### Login Form

```typescript
import { Input, PasswordInput, Button, Alert } from '@/app/components';

function LoginForm() {
  const [error, setError] = useState('');

  return (
    <form onSubmit={handleSubmit}>
      {error && (
        <ErrorAlert
          title="Login Failed"
          description={error}
          dismissible
          onClose={() => setError('')}
        />
      )}

      <Input
        label="Email"
        type="email"
        placeholder="you@example.com"
        fullWidth
        required
      />

      <PasswordInput
        label="Password"
        fullWidth
        required
      />

      <Button
        type="submit"
        variant="primary"
        fullWidth
        isLoading={isSubmitting}
      >
        Sign In
      </Button>
    </form>
  );
}
```

### Dashboard Metrics

```typescript
import { MetricCard } from '@/app/components';

function Dashboard() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <MetricCard
        title="Total Users"
        value="12,345"
        icon={<UsersIcon />}
        color="blue"
        trend="up"
        trendValue="8.2%"
      />
      <MetricCard
        title="Revenue"
        value="$45,231"
        icon={<DollarSignIcon />}
        color="green"
        trend="up"
        trendValue="12.5%"
      />
      <MetricCard
        title="Active Sessions"
        value="892"
        icon={<ActivityIcon />}
        color="purple"
        trend="neutral"
      />
      <MetricCard
        title="Error Rate"
        value="0.3%"
        icon={<AlertTriangleIcon />}
        color="red"
        trend="down"
        trendValue="2.1%"
      />
    </div>
  );
}
```

### Settings Panel with Tabs

```typescript
import {
  Tabs,
  TabList,
  Tab,
  TabPanels,
  TabPanel,
  Card,
  Button
} from '@/app/components';

function SettingsPanel() {
  return (
    <Card>
      <Tabs defaultValue="general">
        <TabList>
          <Tab value="general">General</Tab>
          <Tab value="security">Security</Tab>
          <Tab value="notifications">Notifications</Tab>
        </TabList>

        <TabPanels>
          <TabPanel value="general">
            <GeneralSettings />
          </TabPanel>
          <TabPanel value="security">
            <SecuritySettings />
          </TabPanel>
          <TabPanel value="notifications">
            <NotificationSettings />
          </TabPanel>
        </TabPanels>
      </Tabs>
    </Card>
  );
}
```

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

When adding new components:

1. Follow existing patterns (TypeScript, "use client", props interface)
2. Include accessibility features
3. Add to central `index.ts` export
4. Document in this README
5. Add usage examples

## Phase 1 Complete ✅

All Phase 1 priority components are implemented:
- ✅ Button
- ✅ Input
- ✅ Card
- ✅ MetricCard
- ✅ Modal
- ✅ Badge
- ✅ Dropdown
- ✅ Tabs
- ✅ Tooltip
- ✅ Alert
- ✅ Spinner

See `/Users/rish2jain/Documents/Hackathons/ConsultantOS/claudedocs/MISSING_FRONTEND_COMPONENTS.md` for Phase 2-4 roadmap.
